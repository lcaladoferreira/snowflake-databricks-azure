# Security Policy

## Supported Versions

The following versions of this project are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you believe you have found a security vulnerability, please report it to us as soon as possible.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

- **Private Vulnerability Reporting**: Use the [GitHub Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-receiving-reports-about-vulnerabilities-in-your-repository/reporting-a-vulnerability-in-a-repository) feature if enabled for this repository.
- **Email**: Send an email to `contato@lcfconsulting.com.br` with a detailed description of the vulnerability, steps to reproduce it, and any potential impact.

We will acknowledge receipt of your report within 48 hours and work with you to resolve the issue in a timely manner.

## Security Architecture

### Credential Management
This project enforces strict credential separation:
- **Local Development**: Use a `.env` file (never committed, enforced by `.gitignore`).
- **Production**: Credentials must be stored in **Azure Key Vault**. Databricks Secret Scopes should be used to reference these secrets without exposing them in code.

### IAM Recommendations
- **Azure**: Use Service Principals with the `Storage Blob Data Contributor` role for ADLS Gen2 access.
- **Snowflake**: Use a dedicated `MIGRATION_ROLE` with `USAGE` on the database/schema and `SELECT` on the required tables. Use Key-Pair authentication for production extractors.
