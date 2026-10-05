# ODBP-3

Issuer-bound device uniqueness: one wallet has one active spend root. A second device cannot be provisioned for the same wallet. Replacement is an issuer-mediated migration and the old device is revoked.

This closes duplicate provisioning. It does not defeat a physically cloned Secure Element; that requires genuine non-exportable hardware and secure provisioning.