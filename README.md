# Cryptanalysis on ECC-based Algorithms
**Contibutions:**
- Phan Nguyễn Việt Bắc - 23520087
- Trần Gia Bảo         - 23520139
- Châu Hoàng Phúc - 23521191

**Affiliation:**
Universiry of Information Technology

**Course Information:**
NT219.P22.ANTT - Cryptography

**Lecturer:** 
Nguyễn Ngọc Tự

## Overview
Elliptic Curve Cryptography (ECC) uses the algebraic structure of elliptic curves over finite fields to provide secure public-key cryptographic schemes. Compared to RSA, ECC achieves equivalent security with shorter key lengths, enabling faster computation and lower resource usage, making it ideal for mobile devices, embedded systems, and blockchain technologies.

## Key Components
- **Mathematical Background**: Covers elliptic curve definitions, point addition, scalar multiplication, curve order, subgroup order, and the Elliptic Curve Discrete Logarithm Problem (ECDLP), the foundation of ECC security.
- **Applications**: Includes:
  - **ECDH** (Elliptic Curve Diffie-Hellman): For secure key exchange.
  - **ECDSA** (Elliptic Curve Digital Signature Algorithm): For verifying message authenticity and integrity.
  - **ECIES** (Elliptic Curve Integrated Encryption Scheme): For encryption.
- **Tools**: Uses SageMath, Python 3.x, and PyCryptodome for cryptographic operations and analysis.

## Attack Types on ECC
ECC security relies on the hardness of the ECDLP, but vulnerabilities arise from poor curve selection, implementation flaws, or parameter manipulation. Below are the key attack types detailed in the report:

### 1. ECDH Attacks
- **Small Order Curve Attack**:
  - **Description**: Occurs when the generator point has a small order \( n \), making the ECDLP easier to solve.
  - **Method**: Attackers use algorithms like Baby-Step Giant-Step (BSGS) or Pollard's Rho, with complexity \( O(\sqrt{n}) \), to recover the private key.
  - **Impact**: If \( n \) is small, the key exchange becomes vulnerable, allowing attackers to deduce the shared secret.
- **Smooth Order Curve Attack**:
  - **Description**: Targets curves where the order \( n \) is composite with small prime factors (smooth), enabling the Pohlig-Hellman algorithm.
  - **Method**: Solves the ECDLP for each prime factor using BSGS or Pollard's Rho, then combines results via the Chinese Remainder Theorem (CRT). Complexity is roughly \( O(\sqrt{p_{\text{max}}}) \), where \( p_{\text{max}} \) is the largest prime factor.
  - **Impact**: Reduces attack complexity significantly (e.g., from \( 2^{64} \) to \( 2^{15} \) for a 128-bit order with a 30-bit largest prime factor).
- **Invalid Curve Attack**:
  - **Description**: Exploits systems that fail to validate if a point lies on the agreed curve. An attacker provides a point on a different curve \( \tilde{E} \) with a smooth order.
  - **Method**: The server computes operations on \( \tilde{E} \), leaking information about the private key modulo small subgroup orders. CRT combines these to recover the full key.
  - **Impact**: Can fully compromise the private key if multiple malicious curves are used.
- **Singular Elliptic Curves**:
  - **Description**: Targets curves with a discriminant \( \Delta = -(4A^3 + 27B^2) \equiv 0 \pmod{p} \), making them singular (e.g., cusps or nodes).
  - **Method**: 
    - **Cusp**: Maps the ECDLP to a trivial additive group problem in \( \mathbb{F}_p \).
    - **Node**: Maps to a multiplicative group DLP in \( \mathbb{F}_p^* \), solvable with algorithms like Index Calculus if \( p-1 \) is smooth.
  - **Impact**: Reduces ECDLP to an easily solvable problem, breaking security.
- **Supersingular Curves (MOV Attack)**:
  - **Description**: Targets curves with a small embedding degree \( k \), reducing the ECDLP to a standard DLP in a finite field \( \mathbb{F}_{p^k} \).
  - **Method**: Uses bilinear pairings (e.g., Weil pairing) to map the ECDLP to a DLP solvable with algorithms like Index Calculus if \( k \) is small (e.g., \( k \leq 6 \)).
  - **Impact**: Makes the ECDLP significantly easier, especially for supersingular curves.
- **Anomalous Curves (Smart Attack)**:
  - **Description**: Applies to curves where the number of points equals the field size (\( \#E(\mathbb{F}_p) = p \)).
  - **Method**: Lifts points to p-adic numbers and uses the p-adic elliptic logarithm to solve the ECDLP in linear time (\( O(\log p) \)).
  - **Impact**: Completely breaks the ECDLP for such curves, making them unusable for cryptography.

### 2. ECDSA Vulnerabilities
- **Not Hashing the Message**:
  - **Description**: If the message is not fully hashed (e.g., only a prefix is used), attackers can append malicious data without invalidating the signature.
  - **Impact**: Compromises message integrity, allowing forged messages to pass verification.
- **Nonce Reuse**:
  - **Description**: Using the same nonce \( k \) for two signatures with different messages exposes the private key.
  - **Method**: From two signatures with the same \( r \), the attacker solves linear equations to recover \( k \) and then the private key \( d_A \).
  - **Impact**: Famously exploited in the Sony PlayStation 3 hack (2010), leading to full key recovery.
- **Biased Nonce and Lattice Attacks**:
  - **Description**: Occurs when nonces are not uniformly random (e.g., predictable bits or small range), allowing lattice-based attacks.
  - **Method**: Collects multiple signatures and constructs a lattice to solve the Hidden Number Problem (HNP) using the LLL algorithm, recovering the private key.
  - **Impact**: Even small biases (e.g., 2-3 predictable bits) can lead to key recovery with enough signatures.

## Proposed Solutions
- **ECDH**:
  - Use standardized curves (e.g., Curve25519, NIST P-256) to avoid weak parameters.
  - Validate all points to ensure they lie on the correct curve and subgroup.
  - Use ephemeral keys (ECDHE) for forward secrecy.
- **ECDSA**:
  - Hash the entire message to prevent manipulation.
  - Use deterministic nonce generation (RFC 6979) to eliminate nonce reuse and bias.
  - Employ cryptographically secure random number generators (CSPRNGs) if random nonces are used.
- **General**:
  - Regularly update cryptographic libraries (e.g., OpenSSL, libsodium).
  - Conduct security audits and penetration testing.
  - Choose modern curves like Curve25519/Ed25519 for enhanced security and efficiency.

## Deployment Recommendations
- **Curve Selection**: Use vetted curves like Curve25519 (X25519 for ECDH, Ed25519 for signatures) or NIST P-curves, as per NIST FIPS 186-4 and SECG SEC 2.
- **Input Validation**: Strictly validate all points and parameters to counter invalid curve attacks.
- **Security Maintenance**: Keep cryptographic implementations updated and monitor new cryptanalysis research.
- **Interoperability**: Select curves based on compatibility with existing systems while prioritizing security.

## References
- Hankerson, D., Menezes, A. J., & Vanstone, S. A. (2004). *Guide to Elliptic Curve Cryptography*.
- NIST FIPS 186-4, SP 800-56A, SECG SEC 2.
- Bernstein, D. J. (2006). *Curve25519: New Diffie-Hellman Speed Records*.
- SafeCurves: https://safecurves.cr.yp.to

For a detailed analysis, refer to the full report.