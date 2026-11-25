# Least-privilege CI/CD read-only policy for Lab 4 application secrets
path "secret/data/lab4/*" {
  capabilities = ["read"]
}
path "secret/metadata/lab4/*" {
  capabilities = ["list", "read"]
}
