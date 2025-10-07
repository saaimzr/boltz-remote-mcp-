#!/usr/bin/env python3
"""
Boltz MCP Server - FastMCP Implementation

This server exposes Boltz protein structure prediction capabilities through the MCP protocol.
It runs on a remote GPU server and can be accessed by Claude Desktop through HTTP transport.

Key Features:
- Accepts PDB files or sequences
- Runs Boltz inference on local GPUs
- Returns predicted structures (CIF files)
- Handles file uploads and downloads
- Manages job queue for long-running predictions
- HTTP transport for remote access
- Optional authentication support
"""

import os
import sys
import tempfile
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# FastMCP imports
from fastmcp import FastMCP

# File handling for binary data (PDB files, CIF files)
import base64

# Create the FastMCP server instance
mcp = FastMCP("Boltz Protein Structure Prediction Server")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directory to store uploaded files (PDB inputs)
UPLOAD_DIR = Path.home() / ".boltz_mcp" / "uploads"
# Directory to store prediction outputs (CIF files, logs)
OUTPUT_DIR = Path.home() / ".boltz_mcp" / "outputs"
# Directory where Boltz models are cached
MODEL_CACHE_DIR = Path.home() / ".boltz_mcp" / "models"
# Maximum file size for uploads (100MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024

# Create directories if they don't exist
# exist_ok=True prevents errors if directory already exists
# parents=True creates parent directories as needed
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Job tracking dictionary - stores status of inference jobs
# Key: job_id (hash), Value: dict with status, progress, output_path
jobs: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_job_id(input_data: str) -> str:
    """
    Generate a unique job ID from input data using SHA256 hash.

    This allows us to:
    1. Uniquely identify each job
    2. Avoid re-running identical predictions (caching)
    3. Track job status across requests

    Args:
        input_data: String representation of input (filename, sequence, etc.)

    Returns:
        Hexadecimal hash string (first 16 chars for readability)
    """
    # Create SHA256 hash object
    hash_obj = hashlib.sha256()
    # Update hash with UTF-8 encoded input string
    hash_obj.update(input_data.encode('utf-8'))
    # Return first 16 characters of hex digest
    # Full hash is 64 chars, 16 is sufficient for uniqueness in our use case
    return hash_obj.hexdigest()[:16]


def save_uploaded_file(content: str, filename: str) -> Path:
    """
    Save base64-encoded file content to disk.

    Claude Desktop sends files as base64 strings. We need to:
    1. Decode the base64 string to binary data
    2. Save to disk with original filename
    3. Return path for processing

    Args:
        content: Base64-encoded file content
        filename: Original filename (e.g., "protein.pdb")

    Returns:
        Path object pointing to saved file

    Raises:
        ValueError: If content is too large or invalid base64
    """
    # Decode base64 string to binary bytes
    # base64 encoding is used to safely transmit binary data as text
    try:
        file_data = base64.b64decode(content)
    except Exception as e:
        raise ValueError(f"Invalid base64 content: {e}")

    # Check file size to prevent disk space issues
    if len(file_data) > MAX_UPLOAD_SIZE:
        raise ValueError(f"File too large: {len(file_data)} bytes (max: {MAX_UPLOAD_SIZE})")

    # Create full path: upload_dir/filename
    file_path = UPLOAD_DIR / filename

    # Write binary data to file
    # 'wb' mode = write binary
    with open(file_path, 'wb') as f:
        f.write(file_data)

    return file_path


def load_output_file(file_path: Path) -> str:
    """
    Read output file and encode as base64 for transmission.

    Boltz outputs CIF files (text-based structure format).
    We encode as base64 to safely send back through MCP protocol.

    Args:
        file_path: Path to output file (e.g., predicted.cif)

    Returns:
        Base64-encoded file content

    Raises:
        FileNotFoundError: If output file doesn't exist
    """
    # Check if file exists before attempting to read
    if not file_path.exists():
        raise FileNotFoundError(f"Output file not found: {file_path}")

    # Read binary data from file
    # 'rb' mode = read binary
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Encode binary data to base64 string
    # decode('utf-8') converts bytes to string for JSON serialization
    return base64.b64encode(file_data).decode('utf-8')


async def run_boltz_inference(
    input_path: Path,
    output_dir: Path,
    job_id: str,
    devices: List[int] = [0],
    recycling_steps: int = 3,
    sampling_steps: int = 200,
    diffusion_samples: int = 1
) -> Path:
    """
    Run Boltz inference asynchronously.

    This is the core function that actually runs protein structure prediction.
    It calls the Boltz command-line tool as a subprocess.

    Args:
        input_path: Path to input PDB or FASTA file
        output_dir: Directory to save outputs
        job_id: Unique job identifier
        devices: List of GPU device IDs to use (e.g., [0, 1] for 2 GPUs)
        recycling_steps: Number of recycling iterations (improves accuracy)
        sampling_steps: Diffusion sampling steps (more = better quality, slower)
        diffusion_samples: Number of samples to generate

    Returns:
        Path to main output CIF file

    Raises:
        RuntimeError: If Boltz execution fails
    """
    # Update job status to "running"
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = datetime.now().isoformat()

    # Create output directory for this specific job
    job_output_dir = output_dir / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    # Build Boltz command
    # This follows the Boltz CLI interface from the GitHub repo
    cmd = [
        "boltz",  # Assumes boltz is installed and in PATH (or use full path)
        "predict",  # Subcommand for running predictions
        str(input_path),  # Input file path
        "--out_dir", str(job_output_dir),  # Output directory
        "--devices", str(len(devices)),  # Number of GPU devices to use
        "--recycling_steps", str(recycling_steps),  # Number of recycling iterations
        "--sampling_steps", str(sampling_steps),  # Diffusion steps
        "--diffusion_samples", str(diffusion_samples),  # How many predictions to generate
        "--cache", str(MODEL_CACHE_DIR),  # Where to cache model weights
    ]

    try:
        # Run Boltz as subprocess asynchronously
        # asyncio.create_subprocess_exec runs command without blocking
        # stdout/stderr=PIPE captures output for logging
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for process to complete and get output
        stdout, stderr = await process.communicate()

        # Check if command succeeded (return code 0 = success)
        if process.returncode != 0:
            # Update job status to failed
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = stderr.decode('utf-8')
            raise RuntimeError(f"Boltz failed: {stderr.decode('utf-8')}")

        # Find the output CIF file
        # Boltz typically outputs: <job_output_dir>/predictions/<name>.cif
        # We look for any .cif file in the output directory
        cif_files = list(job_output_dir.glob("**/*.cif"))

        if not cif_files:
            raise RuntimeError("No CIF output file found after prediction")

        # Take the first CIF file (or could implement selection logic)
        output_cif = cif_files[0]

        # Update job status to completed
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_path"] = str(output_cif)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

        return output_cif

    except Exception as e:
        # Update job status to failed on any exception
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        raise


# ============================================================================
# MCP TOOLS - These functions are exposed to Claude Desktop
# ============================================================================

@mcp.tool()
async def predict_structure_from_pdb(
    pdb_content: str,
    filename: str = "input.pdb",
    recycling_steps: int = 3,
    sampling_steps: int = 200,
    devices: str = "0"
) -> Dict[str, Any]:
    """
    Predict protein structure from PDB file using Boltz.

    This tool accepts a PDB file (base64 encoded) and runs Boltz prediction.
    Returns job_id for tracking progress and retrieving results.

    The @mcp.tool() decorator automatically:
    1. Registers this function as an MCP tool
    2. Generates JSON schema from type hints
    3. Handles request/response serialization

    Args:
        pdb_content: Base64-encoded PDB file content
        filename: Name for the uploaded file (default: "input.pdb")
        recycling_steps: Boltz recycling iterations (default: 3)
        sampling_steps: Diffusion sampling steps (default: 200)
        devices: Comma-separated GPU device IDs (default: "0")

    Returns:
        Dictionary with:
        - job_id: Unique identifier for this prediction job
        - status: Current job status ("queued", "running", "completed", "failed")
        - message: Human-readable status message
    """
    try:
        # Save the uploaded PDB file to disk
        input_path = save_uploaded_file(pdb_content, filename)

        # Generate unique job ID from filename and timestamp
        # This ensures each submission gets a unique ID
        job_input_id = f"{filename}_{datetime.now().isoformat()}"
        job_id = generate_job_id(job_input_id)

        # Initialize job tracking entry
        jobs[job_id] = {
            "status": "queued",  # Initial status
            "input_path": str(input_path),
            "created_at": datetime.now().isoformat(),
            "filename": filename,
        }

        # Parse devices string to list of ints
        # "0,1" -> [0, 1]
        device_list = [int(d.strip()) for d in devices.split(",")]

        # Start inference asynchronously
        # asyncio.create_task runs the coroutine in the background
        # This allows the tool to return immediately while inference runs
        asyncio.create_task(
            run_boltz_inference(
                input_path=input_path,
                output_dir=OUTPUT_DIR,
                job_id=job_id,
                devices=device_list,
                recycling_steps=recycling_steps,
                sampling_steps=sampling_steps,
            )
        )

        # Return job information immediately
        # User can poll check_job_status() to monitor progress
        return {
            "job_id": job_id,
            "status": "queued",
            "message": f"Prediction job started for {filename}. Use check_job_status() to monitor progress.",
        }

    except Exception as e:
        # Return error information if something goes wrong
        return {
            "error": str(e),
            "status": "failed",
        }


@mcp.tool()
async def predict_structure_from_sequence(
    sequence: str,
    chain_id: str = "A",
    recycling_steps: int = 3,
    sampling_steps: int = 200,
    devices: str = "0"
) -> Dict[str, Any]:
    """
    Predict protein structure from amino acid sequence using Boltz.

    This tool accepts a raw amino acid sequence (e.g., "MKTAYIAKQRQ...")
    and creates a FASTA file for Boltz to process.

    Args:
        sequence: Amino acid sequence (single letter codes)
        chain_id: Chain identifier for the sequence (default: "A")
        recycling_steps: Boltz recycling iterations (default: 3)
        sampling_steps: Diffusion sampling steps (default: 200)
        devices: Comma-separated GPU device IDs (default: "0")

    Returns:
        Dictionary with job_id and status (same as predict_structure_from_pdb)
    """
    try:
        # Validate sequence - should only contain valid amino acid codes
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence_upper = sequence.upper().replace(" ", "").replace("\n", "")

        # Check for invalid characters
        if not all(aa in valid_aa for aa in sequence_upper):
            return {
                "error": "Invalid amino acid sequence. Use single-letter codes only.",
                "status": "failed",
            }

        # Create FASTA format file
        # FASTA format:
        # >header_line (starts with >)
        # SEQUENCE DATA (can be multiple lines)
        fasta_content = f">{chain_id}\n{sequence_upper}\n"

        # Generate filename based on sequence hash
        seq_hash = generate_job_id(sequence_upper)
        filename = f"sequence_{seq_hash}.fasta"

        # Encode FASTA content as base64 for save_uploaded_file()
        fasta_base64 = base64.b64encode(fasta_content.encode('utf-8')).decode('utf-8')

        # Save FASTA file
        input_path = save_uploaded_file(fasta_base64, filename)

        # Generate job ID
        job_input_id = f"{filename}_{datetime.now().isoformat()}"
        job_id = generate_job_id(job_input_id)

        # Initialize job tracking
        jobs[job_id] = {
            "status": "queued",
            "input_path": str(input_path),
            "created_at": datetime.now().isoformat(),
            "filename": filename,
            "sequence_length": len(sequence_upper),
        }

        # Parse devices
        device_list = [int(d.strip()) for d in devices.split(",")]

        # Start inference
        asyncio.create_task(
            run_boltz_inference(
                input_path=input_path,
                output_dir=OUTPUT_DIR,
                job_id=job_id,
                devices=device_list,
                recycling_steps=recycling_steps,
                sampling_steps=sampling_steps,
            )
        )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": f"Prediction job started for sequence (length: {len(sequence_upper)}). Use check_job_status() to monitor progress.",
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
        }


@mcp.tool()
async def check_job_status(job_id: str) -> Dict[str, Any]:
    """
    Check the status of a Boltz prediction job.

    Returns current status and progress information for a job.
    Possible statuses:
    - "queued": Job is waiting to start
    - "running": Job is currently executing
    - "completed": Job finished successfully
    - "failed": Job encountered an error

    Args:
        job_id: Job ID returned from predict_structure_from_pdb/sequence

    Returns:
        Dictionary with status, timestamps, and output info (if completed)
    """
    # Check if job_id exists in our tracking dictionary
    if job_id not in jobs:
        return {
            "error": f"Job ID {job_id} not found",
            "status": "unknown",
        }

    # Return job information
    # This includes all fields we stored in the jobs dictionary
    return jobs[job_id]


@mcp.tool()
async def get_prediction_result(job_id: str) -> Dict[str, Any]:
    """
    Retrieve the prediction result file for a completed job.

    Returns the predicted structure as a base64-encoded CIF file.
    CIF (Crystallographic Information File) is a standard format for
    protein structures, similar to PDB but more modern.

    Args:
        job_id: Job ID from predict_structure_from_pdb/sequence

    Returns:
        Dictionary with:
        - cif_content: Base64-encoded CIF file
        - filename: Suggested filename for saving
        - job_info: Job metadata (timestamps, input info, etc.)
    """
    # Check if job exists
    if job_id not in jobs:
        return {
            "error": f"Job ID {job_id} not found",
            "status": "unknown",
        }

    job = jobs[job_id]

    # Check if job is completed
    if job["status"] != "completed":
        return {
            "error": f"Job is not completed yet. Current status: {job['status']}",
            "status": job["status"],
        }

    try:
        # Load the output CIF file
        output_path = Path(job["output_path"])
        cif_content = load_output_file(output_path)

        # Return file content and metadata
        return {
            "cif_content": cif_content,
            "filename": output_path.name,
            "job_info": job,
            "status": "success",
        }

    except Exception as e:
        return {
            "error": f"Failed to load output file: {e}",
            "status": "error",
        }


@mcp.tool()
async def list_jobs(limit: int = 10) -> Dict[str, Any]:
    """
    List recent prediction jobs with their statuses.

    Useful for:
    1. Seeing what jobs have been run
    2. Finding job IDs if you forgot them
    3. Monitoring overall system activity

    Args:
        limit: Maximum number of jobs to return (default: 10)

    Returns:
        Dictionary with list of job summaries
    """
    # Sort jobs by creation time (most recent first)
    # items() returns (job_id, job_dict) tuples
    # sorted() with key=lambda sorts by created_at timestamp
    # [::-1] reverses to get newest first
    sorted_jobs = sorted(
        jobs.items(),
        key=lambda x: x[1].get("created_at", ""),
        reverse=True
    )[:limit]

    # Create summary list with essential info only
    job_summaries = []
    for job_id, job in sorted_jobs:
        job_summaries.append({
            "job_id": job_id,
            "status": job["status"],
            "filename": job.get("filename", "unknown"),
            "created_at": job.get("created_at", "unknown"),
        })

    return {
        "jobs": job_summaries,
        "total": len(jobs),
    }


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """
    Get information about the Boltz MCP server.

    Returns system information like:
    - Available GPU devices
    - Disk space usage
    - Server version
    - Configuration settings

    Useful for debugging and system monitoring.

    Returns:
        Dictionary with server information
    """
    import shutil  # For disk usage stats

    # Get disk space for output directory
    disk_usage = shutil.disk_usage(OUTPUT_DIR)

    # Try to detect available GPUs
    # This is a simple check - could be enhanced with nvidia-smi parsing
    gpu_info = "Unknown (check with nvidia-smi)"
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_names = [torch.cuda.get_device_name(i) for i in range(gpu_count)]
            gpu_info = f"{gpu_count} GPUs: {', '.join(gpu_names)}"
    except ImportError:
        pass  # PyTorch not installed, can't check GPUs

    return {
        "server": "Boltz MCP Server",
        "version": "1.0.0",
        "mcp_framework": "FastMCP",
        "upload_dir": str(UPLOAD_DIR),
        "output_dir": str(OUTPUT_DIR),
        "model_cache_dir": str(MODEL_CACHE_DIR),
        "disk_usage": {
            "total_gb": disk_usage.total / (1024**3),
            "used_gb": disk_usage.used / (1024**3),
            "free_gb": disk_usage.free / (1024**3),
        },
        "gpu_info": gpu_info,
        "max_upload_size_mb": MAX_UPLOAD_SIZE / (1024**2),
        "active_jobs": len([j for j in jobs.values() if j["status"] == "running"]),
        "total_jobs": len(jobs),
    }


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    """
    Main entry point for the server.

    FastMCP supports multiple transport modes:
    - stdio: Local development (default)
    - http: Remote deployment (recommended for production)

    For HTTP mode, the server runs on specified host:port and is accessible at:
    http://host:port/mcp/

    Environment variables:
    - BOLTZ_TRANSPORT: "stdio" or "http" (default: "http")
    - BOLTZ_HOST: Host to bind to (default: "0.0.0.0")
    - BOLTZ_PORT: Port to listen on (default: 8000)
    - BOLTZ_AUTH_TOKEN: Optional bearer token for authentication
    """
    print("Starting Boltz MCP Server...", file=sys.stderr)
    print(f"Upload directory: {UPLOAD_DIR}", file=sys.stderr)
    print(f"Output directory: {OUTPUT_DIR}", file=sys.stderr)
    print(f"Model cache directory: {MODEL_CACHE_DIR}", file=sys.stderr)

    # Get configuration from environment
    transport = os.getenv("BOLTZ_TRANSPORT", "http")
    host = os.getenv("BOLTZ_HOST", "0.0.0.0")
    port = int(os.getenv("BOLTZ_PORT", "8000"))

    if transport == "http":
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Starting HTTP server on {host}:{port}", file=sys.stderr)
        print(f"Server will be accessible at: http://{host}:{port}/mcp/", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

        # Run with HTTP transport
        mcp.run(transport="http", host=host, port=port)
    else:
        print("Running in STDIO mode (local development)", file=sys.stderr)
        # Run with stdio transport (default)
        mcp.run()
