---
name: winnco-gnn-architect
description: Blueprint and architectural guidelines for designing, training, and troubleshooting Graph Neural Networks (GNNs) on the massive WinnCo Heterogeneous Dataset.
---

# WinnCo GNN Architect Guidelines

This skill provides the authoritative blueprint for building Graph Neural Networks specifically for the WinnCo dataset. Future agents modifying or implementing GNN pipelines for WinnCo must adhere strictly to these architectural constraints and best practices.

## 1. The Dataset (Scale & Topology)
The WinnCo dataset is a massive, highly-connected Heterogeneous Graph representing real estate, leasing, and financial records.
- **Scale:** ~24 Million Nodes, ~160 Million Edges.
- **Core Nodes:** `Tenant`, `Unit`, `Ledger`, `Lease`, `GuestCard`, `Member`.
- **Core Relations:** `APPLIED_TO`, `BILLED_FOR`, `HAS_GUESTCARD`, `HAS_MEMBER`, `SIGNS`, `RESIDES_IN`.
- **Data Loaders:** Always utilize `load_graph_data()` from `src/graph/graph_dataset.py` which parses the silver-tier parquet files into a `torch_geometric.data.HeteroData` object.

## 2. Hardware Constraints (Apple Silicon / MPS)
The primary execution environment is Apple Silicon using the Metal Performance Shaders (`mps`) backend.
- **The OOM Danger:** The graph is vastly too large to fit in unified memory for dense tensor operations. Standard Full-Batch GNN message passing will instantly crash with Out Of Memory (OOM) errors.
- **C++ Extensions:** Advanced PyTorch Geometric sampling features require `torch-sparse` and `torch-scatter` C++ extensions compiled specifically for Apple Silicon. Ensure they are installed via `--no-build-isolation` if missing.

## 3. Parallel Architectures (Plug & Play)
WinnCo currently supports two parallel GNN training paradigms. Agents must explicitly choose which paradigm to build upon based on the goal:

### Paradigm A: Full-Batch with DropEdge (`train_autoencoder.py`)
- **How it works:** Loads the entire graph onto the GPU but aggressively subsamples (drops 80% of edges) during the forward pass to artificially cap memory consumption.
- **Pros:** Fast epoch times, simpler code structure.
- **Cons:** Significantly degraded structural accuracy due to disconnected neighborhoods. Inference must be chunked and moved to the CPU.

### Paradigm B: Mini-Batch Sampling (`train_autoencoder_minibatch.py`)
- **How it works:** Uses `torch_geometric.loader.LinkNeighborLoader` to dynamically sample localized 2-hop neighborhoods (e.g., `num_neighbors=[10, 5]`) for training batches.
- **Pros:** True mathematical fidelity (100% of edges are processed over the epoch), highly scalable, handles 22M+ edge relations (like `APPLIED_TO`) natively on GPU without OOM.
- **Cons:** Extremely slow initialization and slower epoch times. Requires `torch-sparse` backend.
- **Optimization Rules:** When running anomaly extraction inference, always maximize batch sizes (`INFER_BATCH_SIZE=8192`) and utilize multiprocessing (`num_workers=4`) to drastically reduce inference time.

## 4. Execution Abstraction
To trigger GNN training, always use the unified entry point: `run_gnn.sh`.
- By default, it runs the Legacy Full-Batch model.
- To execute the Mini-Batch architecture, prefix with the environment flag: `USE_MINIBATCH=1 ./run_gnn.sh`.

## 5. Coding Standards
- **Loss Function:** `binary_cross_entropy_with_logits` is standard for edge reconstruction.
- **Debugging:** Due to Python buffering, always prefix long-running pipeline execution with `PYTHONUNBUFFERED=1` to prevent silent hangs in the terminal.
- **Outputs:** Anomaly outputs must be exported as CSVs to `WinnCo Dataset/graph_out/anomalies/` and sorted by `surprisal` descending.
