# Boltz MCP Usage Examples

This guide provides practical examples of computational biology workflows using the Boltz remote MCP server through Claude Desktop.

## Example 1: Predict Structure from Amino Acid Sequence

### Scenario
You have a protein sequence and want to predict its 3D structure.

### Workflow

**Step 1: Start with your sequence**

```
I have this protein sequence and I want to predict its structure:

MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL

Can you use Boltz to predict its structure?
```

**Step 2: Claude will call the MCP tool**

Claude will automatically:
1. Call `predict_structure_from_sequence` tool
2. Send your sequence to the remote server
3. Return a job ID

Example response:
```
I've submitted your protein sequence for structure prediction using Boltz.

Job ID: abc123def456
Status: queued

The prediction is now running on the lab GPU server. This may take 10-30 minutes depending on sequence length and server load.
```

**Step 3: Check job status**

```
Can you check the status of job abc123def456?
```

Claude will call `check_job_status` and report:
- Current status (queued/running/completed/failed)
- Progress information
- Estimated time remaining (if available)

**Step 4: Retrieve results**

Once completed:
```
The job is completed! Can you get the predicted structure file?
```

Claude will:
1. Call `get_prediction_result`
2. Download the CIF file
3. Offer to save it or analyze it

### Advanced Options

You can customize prediction parameters:

```
Run a high-quality prediction with these parameters:
- Sequence: MKTA... (your sequence)
- Recycling steps: 5 (more accurate)
- Sampling steps: 300 (higher quality)
- Use GPU 1
```

## Example 2: Refine Existing PDB Structure

### Scenario
You have a PDB file from experimental data or AlphaFold, and you want to refine it with Boltz.

### Workflow

**Step 1: Upload PDB file**

In Claude Desktop, you can drag-and-drop or upload a PDB file:

```
I'm uploading this PDB file (protein.pdb). Can you use Boltz to refine/predict its structure?

[Upload: protein.pdb]
```

**Step 2: Claude processes the file**

Claude will:
1. Read the PDB file contents
2. Encode it as base64
3. Call `predict_structure_from_pdb` tool
4. Return job ID

**Step 3: Monitor and retrieve**

Same as Example 1 - check status and get results.

## Example 3: Batch Processing Multiple Sequences

### Scenario
You have multiple protein sequences and want to predict all their structures.

### Workflow

```
I have 5 protein sequences that I need structure predictions for:

Protein 1 (Kinase):
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLS...

Protein 2 (Transcription factor):
MSELVRKQNELQKSLEEAERLGPYVVEKQPLSKKDIKKLHDISLLEKAQ...

Protein 3 (Membrane protein):
MTDQRSELVRRQKELQKSLEEADRLGPYVVEKQPLSKKDIKKLHDISL...

Can you:
1. Submit all of them for structure prediction
2. Track their progress
3. Let me know when each is complete
```

Claude will:
1. Submit each sequence as a separate job
2. Create a tracking list with all job IDs
3. Periodically check status
4. Notify you as each completes

## Example 4: Compare Predicted Structures

### Scenario
You want to compare multiple structure predictions (e.g., wild-type vs mutant).

### Workflow

```
I have two versions of the same protein:

Wild-type:
MKTAYIAKQRQISFVKSHFSRQ...

Mutant (R42A):
MKTAYIAKQAQISFVKSHFSRQ...  (note the R→A mutation at position 42)

Can you:
1. Predict structures for both
2. Once complete, analyze the structural differences
3. Highlight regions affected by the mutation
```

Claude will:
1. Submit both predictions
2. Track both jobs
3. Retrieve both CIF files
4. Perform structural comparison (using built-in analysis or external tools)

## Example 5: Full Workflow with Downstream Analysis

### Scenario
Comprehensive workflow from sequence to visualization.

### Workflow

```
I'm studying a novel enzyme. Here's what I need:

1. Sequence: MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGT...

2. Please:
   - Predict its 3D structure using Boltz
   - Save the CIF file to my desktop
   - Analyze key structural features (domains, secondary structure)
   - Identify potential active sites
   - Suggest similar known structures from PDB

3. Once done, help me prepare this for PyMOL visualization
```

Claude will orchestrate:
1. Structure prediction via Boltz MCP
2. File management (save to desktop)
3. Structural analysis
4. Database searches
5. PyMOL script generation

## Example 6: Using With Other MCP Servers

### Scenario
Combine Boltz MCP with filesystem MCP for automated workflows.

### Setup
Install filesystem MCP alongside Boltz MCP in Claude Desktop config:

```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/client-stdio", "tcp://..."]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    }
  }
}
```

### Workflow

```
I have a project directory at /Users/me/research/proteins/

Please:
1. Read all .fasta files in that directory
2. For each sequence, predict structure using Boltz
3. Save all predicted CIF files back to /Users/me/research/proteins/predictions/
4. Create a summary CSV with:
   - Filename
   - Sequence length
   - Prediction status
   - Output file path
```

Claude will:
1. Use filesystem MCP to read FASTA files
2. Use Boltz MCP to predict structures
3. Use filesystem MCP to save results
4. Create summary report

## Example 7: Interactive Optimization

### Scenario
Iteratively optimize prediction parameters based on results.

### Workflow

```
I want to find optimal prediction parameters for this sequence:
MKTAYIAKQRQISFVKSHFSRQLEERLGLIE...

Let's start with default parameters (recycling_steps=3, sampling_steps=200).
Based on the result quality, we can adjust and re-run.
```

Claude will:
1. Run initial prediction with defaults
2. Retrieve and analyze results
3. Suggest parameter adjustments if needed
4. Re-run with optimized parameters

## Example 8: Multi-Chain Complex Prediction

### Scenario
Predict structure of a protein complex (multiple chains).

### Workflow

```
I have a protein complex with two chains:

Chain A (Receptor):
MKTAYIAKQRQISFVKSHFSRQLEERLGLIE...

Chain B (Ligand):
MSELVRKQNELQKSLEEAERLGP...

Can you predict the complex structure? Please use FASTA format with both chains.
```

Claude will:
1. Create multi-chain FASTA format
2. Submit to Boltz (which supports multimers)
3. Retrieve complex structure

## Example 9: Error Recovery

### Scenario
Handling failed predictions gracefully.

### Workflow

```
Check the status of job xyz789.
If it failed, can you:
1. Tell me why it failed
2. Suggest parameter adjustments
3. Retry with corrected parameters
```

Claude will:
1. Call `check_job_status`
2. Parse error messages
3. Diagnose issues (e.g., sequence too long, OOM)
4. Suggest solutions (e.g., reduce sampling_steps)
5. Retry automatically

## Example 10: Monitoring Server Resources

### Scenario
Check server capacity before submitting large jobs.

### Workflow

```
Before I submit this large batch of predictions:
1. Check the Boltz server status
2. Tell me:
   - How many GPUs are available
   - Current disk space
   - Active jobs
   - System load

If resources are low, I'll wait before submitting.
```

Claude will:
1. Call `get_server_info`
2. Report system status
3. Recommend optimal timing for submission

## Tips for Effective Usage

### 1. Sequence Preparation

**Good:**
```
MKTAYIAKQRQISFVKSHFSRQ
```

**Bad (has spaces/line numbers):**
```
1  MKTAYIAK
10 QRQISFVK
20 SHFSRQ
```

Claude can clean this, but it's better to provide clean sequences.

### 2. Job Management

Keep track of job IDs:
```
Please create a list of all my running jobs and their statuses.
```

### 3. Parameter Selection

- **Quick prediction**: recycling_steps=1, sampling_steps=100
- **Standard**: recycling_steps=3, sampling_steps=200 (default)
- **High quality**: recycling_steps=5, sampling_steps=300
- **Maximum quality**: recycling_steps=10, sampling_steps=500

### 4. Handling Long Jobs

```
Submit this prediction, then remind me to check on it in 30 minutes.
```

Claude can set reminders (if supported) or you can check back later.

### 5. Combining with Other Tools

```
After the Boltz prediction completes:
1. Convert CIF to PDB format
2. Run Swiss-Model for comparison
3. Generate PyMOL visualization script
4. Create a comparison report
```

## Common Questions

**Q: Can I cancel a running job?**
A: Not directly through MCP (would require adding a cancel tool). You can ask your lab admin to kill the process.

**Q: How long do predictions take?**
A: Depends on sequence length and parameters:
- Short (<100 AA): 5-15 minutes
- Medium (100-300 AA): 15-45 minutes
- Long (>300 AA): 45+ minutes

**Q: Can I download intermediate results?**
A: Currently, only final CIF files are returned. Could be extended to return confidence plots, attention maps, etc.

**Q: What if the server runs out of disk space?**
A: Use `get_server_info` to monitor. Clean up old jobs if needed.

**Q: Can multiple users use the same server?**
A: Yes! The server handles concurrent requests. Each user gets their own jobs.

## Next Steps

- Explore the MCP protocol documentation
- Check out PyMOL/ChimeraX for visualizing CIF files
- Integrate with other bioinformatics tools
- Contribute improvements to the server code

## Troubleshooting Common Workflows

**Issue: "Job failed with out of memory error"**
```
Retry with:
- Reduced sampling_steps (e.g., 100 instead of 200)
- Use fewer GPUs
- Split large multimers into separate predictions
```

**Issue: "Results look incorrect"**
```
Try:
- Increase recycling_steps for better accuracy
- Check input sequence for errors
- Compare with AlphaFold/ESMFold predictions
```

**Issue: "CIF file won't open in my viewer"**
```
Convert to PDB format:
- Use PyMOL: load CIF, save as PDB
- Use phenix.cif_as_pdb
- Use online converters
```
