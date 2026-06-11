# MiniChain Context

MiniChain is a minimal, educational implementation of a Proof-of-Work (PoW) blockchain written in Python. It includes a P2P network layer, a mempool for transaction management, cryptographic transaction signing, state management with accounts, and a minimal sandboxed smart contract execution environment.

## Architecture & Components

The `minichain` package is composed of the following files, each responsible for a specific part of the blockchain:

- **`__init__.py`**: Exports the primary classes and functions for the package, acting as the public API.
- **`block.py`**: Defines the `Block` class, which handles block structure, deterministic timestamps, Merkle root calculation for transactions, and serialization for mining and hashing.
- **`chain.py`**: Contains the `Blockchain` class which manages the chain of blocks, handles adding new blocks after validating their hashes, and executes transactions against a temporary state to ensure atomicity.
- **`contract.py`**: Implements `ContractMachine`, a minimal, sandboxed Python-based smart contract execution environment. It uses `multiprocessing`, resource limits, and AST validation to restrict available built-ins and prevent malicious code execution.
- **`mempool.py`**: Defines the `Mempool` class, which holds pending valid transactions before they are mined into a block. It handles duplicate prevention, max size limits, and deterministic sorting for block inclusion.
- **`p2p.py`**: Implements a lightweight TCP-based peer-to-peer network (`P2PNetwork`) using `asyncio`. It handles connecting to peers, listening for incoming connections, broadcasting blocks and transactions, and validating incoming JSON messages.
- **`persistence.py`**: Provides utility functions to `save` and `load` the blockchain and state to a local JSON file (`data.json`) atomically. It uses fsync and temp files to prevent corruption and verifies chain integrity on load.
- **`pow.py`**: Contains the Proof-of-Work mining logic (`mine_block` and `calculate_hash`), enforcing difficulty targets, nonces, limits, and optional timeout conditions.
- **`serialization.py`**: Provides helper functions (`canonical_json_dumps`, `canonical_json_bytes`, `canonical_json_hash`) for deterministic JSON serialization, crucial for consistent signature verification and hashing across environments.
- **`state.py`**: Defines the `State` class, which manages account balances, nonces, and contract storage. It evaluates and applies transactions via distinct branches: regular transfers, contract deployments, and contract calls.
- **`transaction.py`**: Defines the `Transaction` class, handling transaction structure, digital signatures using `nacl` (Ed25519), verification, deterministic transaction IDs, and serialization.
- **`validators.py`**: Provides simple validation utilities, such as `is_valid_receiver`, ensuring addresses correspond to standard hex lengths (40 or 64 characters).