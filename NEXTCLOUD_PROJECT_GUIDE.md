# ☁️ Mini Project: Deployment, Configuration and Management of Nextcloud as a Cloud Application

### Academic Submission & Implementation Documentation
**Project Title:** Deployment, Configuration, and Management of Nextcloud as a Private Cloud Application with Enterprise ML Integration  
**Group Work Division:** 4 Team Members  
**Associated Project:** AI-Based Resume Role Detection & Job Readiness Analyzer  

---

## 1. 📌 Executive Summary

Modern enterprises and educational institutions require secure, private, and self-hosted cloud storage environments to preserve data sovereignty, comply with data privacy regulations (e.g., GDPR), and eliminate recurring SaaS subscription costs.

This project implements **Nextcloud** as an enterprise-grade private cloud application using a containerized microservices architecture. It demonstrates:
1. **Containerized Deployment:** Orchestrating Nextcloud, MariaDB, Redis, and a Streamlit AI application using Docker Compose.
2. **System Configuration:** Memory caching with Redis, transactional file locking, PHP upload tuning (up to 16GB), and HTTPS SSL/TLS routing.
3. **Enterprise Management:** Multi-tier user administration, role-based access control (RBAC), storage quota enforcement, collaborative shared folders, and automated disaster recovery.
4. **Machine Learning Pipeline Integration:** Using Nextcloud as a secure candidate resume ingestion repository and analysis report archive for the AI Resume Analyzer.

---

## 2. 🏛️ System Architecture

```
                    ┌────────────────────────────────────────┐
                    │      Clients (Browser / Mobile / Sync) │
                    └───────────────────┬────────────────────┘
                                        │ HTTPS / HTTP
                                        ▼
                         ┌─────────────────────────────┐
                         │   Nextcloud Web Dashboard   │ (Port 8080)
                         └──────────────┬──────────────┘
                                        │ Internal Docker Network (nextcloud-network)
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
│ Nextcloud Core  │ ◄────────► │   Redis Cache   │            │   MariaDB 10.6  │
│ (PHP 8.2+Apache)│            │  (File Locking) │            │  (Metadata DB)  │
└────────┬────────┘            └─────────────────┘            └─────────────────┘
         │
         │ REST / WebDAV API (nextcloud_integration.py)
         ▼
┌─────────────────────────────────┐
│  AI Resume Analyzer Application │ (Port 8501)
│  (Streamlit + Scikit-Learn ML)  │
└─────────────────────────────────┘
```

### Component Breakdown
| Component | Technology | Role in Architecture |
| :--- | :--- | :--- |
| **Cloud Application** | Nextcloud 28+ (Apache) | File synchronization, user management, sharing, app ecosystem. |
| **Relational Database** | MariaDB 10.6 | Stores file indexes, user accounts, permissions, and activity logs. |
| **In-Memory Cache** | Redis (Alpine) | Transactional file locking and distributed memory caching. |
| **AI Application** | Streamlit + Scikit-Learn | Ingests resumes from Nextcloud, runs ML scoring, and saves reports back. |
| **Automation** | Bash & Python | Automated backups (`backup_nextcloud.sh`) and WebDAV sync (`nextcloud_integration.py`). |

---

## 3. 🚀 Phase 1: Deployment Guide

### Prerequisites
* Operating System: Linux (Ubuntu 22.04 LTS / 24.04 LTS recommended) or Windows with Docker Desktop / WSL2.
* Docker Engine 24.0+ and Docker Compose v2.

### Step 1: Prepare Environment File
Copy the provided `.env.nextcloud.example` to `.env`:
```bash
cp .env.nextcloud.example .env
```

### Step 2: Launch the Stack
Run the multi-container stack in detached mode:
```bash
docker compose -f docker-compose.nextcloud.yml up -d
```

### Step 3: Verify Container Health
```bash
docker compose -f docker-compose.nextcloud.yml ps
```
All containers (`nextcloud-app`, `nextcloud-db`, `nextcloud-redis`, and `resume-analyzer-app`) should display status **Up**.

---

## 4. ⚙️ Phase 2: Configuration & Performance Tuning

### 1. Trusted Domains Setup
To allow connections from local networks, domain names, or reverse proxies:
```bash
docker exec -u www-data nextcloud-app php occ config:system:set trusted_domains 1 --value="localhost"
docker exec -u www-data nextcloud-app php occ config:system:set trusted_domains 2 --value="127.0.0.1"
docker exec -u www-data nextcloud-app php occ config:system:set trusted_domains 3 --value="nextcloud-app"
```

### 2. Configure Redis File Locking & APCu Caching
Eliminate Nextcloud admin warnings and prevent race conditions during concurrent uploads:
```bash
docker exec -u www-data nextcloud-app php occ config:system:set filelocking.enabled --value="true" --type=boolean
docker exec -u www-data nextcloud-app php occ config:system:set memcache.locking --value="\OC\Memcache\Redis"
docker exec -u www-data nextcloud-app php occ config:system:set memcache.local --value="\OC\Memcache\APCu"
```

### 3. Expand PHP Memory & File Upload Limits
By default, PHP restricts uploads to 512MB. For enterprise cloud repositories, update to 16GB:
```bash
docker exec -u root nextcloud-app bash -c "echo 'upload_max_filesize=16G' >> /usr/local/etc/php/conf.d/nextcloud.ini"
docker exec -u root nextcloud-app bash -c "echo 'post_max_size=16G' >> /usr/local/etc/php/conf.d/nextcloud.ini"
docker exec -u root nextcloud-app bash -c "echo 'memory_limit=1024M' >> /usr/local/etc/php/conf.d/nextcloud.ini"
docker restart nextcloud-app
```

### 4. Integrate Streamlit via Nextcloud "External Sites" App
1. Log into Nextcloud as **admin** at `http://localhost:8080`.
2. Navigate to **Apps** ➔ Search for **External sites** ➔ Click **Download and enable**.
3. Go to **Administration Settings** ➔ **External sites**.
4. Add:
   * **Name:** `AI Resume Analyzer`
   * **URL:** `http://<SERVER_IP>:8501`
5. The AI Analyzer now appears directly in the Nextcloud navigation bar as an embedded tool!

---

## 5. 👥 Phase 3: Cloud Management & Administration

### 1. Role-Based Access Control (RBAC) & User Groups
Create three distinct user groups in **Administration Settings ➔ Users**:
* **HR_Managers:** Full access to candidate resumes, folders, and reports.
* **Candidates:** Restricted access; can only upload resume files to their assigned drop-box.
* **ML_Engineers:** Access to datasets, model checkpoints, and analytical logs.

### 2. Storage Quota Allocation
To showcase resource governance:
* `HR_Managers`: **50 GB**
* `ML_Engineers`: **20 GB**
* `Candidates`: **200 MB** (Sufficient for resume PDF uploads only).

### 3. Collaborative Sharing & Security Governance
* **Group Folder:** Create a shared folder `Candidate_Resumes` accessible only by `HR_Managers`.
* **Password-Protected Public Link:** Generate a public drop-link for external candidates with:
  * Password protection.
  * Expiration date (e.g., 7 days).
  * Upload-only permission (File Drop mode to ensure candidates cannot view others' resumes).
* **Two-Factor Authentication (2FA):** Enabled for administrator and HR accounts via TOTP.

### 4. Automated Backup & Disaster Recovery
Run the automated backup script to create atomic dumps of database and files:
```bash
chmod +x backup_nextcloud.sh
./backup_nextcloud.sh
```
*Creates timestamped archives in `./backups/` containing `nextcloud_db.sql` and `nextcloud_data.tar.gz`.*

---

## 6. 🤖 Phase 4: Integration with AI Resume Analyzer

The Python script `nextcloud_integration.py` links Nextcloud to the ML pipeline:
1. Candidates upload resumes to Nextcloud's `/Resumes` folder.
2. The ML pipeline queries Nextcloud via WebDAV API, downloads unanalyzed PDFs.
3. The model extracts text via `pdfplumber`, predicts the job role using the Linear SVM model, and computes the Job Readiness Score.
4. The system formats an evaluation report and uploads it to `/Candidate_Reports` in Nextcloud.

---

## 7. 🤝 Phase 5: Group Work Division Matrix

| Member | Role / Designation | Assigned Project Deliverables |
| :--- | :--- | :--- |
| **Member 1 (Lead)** | **Cloud & Virtualization Architect** | • Host VM provisioning & network security groups.<br>• Docker Compose multi-container setup (`docker-compose.nextcloud.yml`).<br>• Docker volume persistence and container health checks. |
| **Member 2** | **System & Database Administrator** | • MariaDB configuration, character sets, and tuning.<br>• Redis caching integration & OCC command-line configuration.<br>• PHP upload limits and trusted domains tuning. |
| **Member 3** | **Security & Access Control Manager** | • User groups, roles, and storage quotas.<br>• External Sites app integration (embedding Streamlit).<br>• Password-protected public sharing and 2FA authentication. |
| **Member 4** | **Disaster Recovery & Integration Engineer** | • Automated backup & restoration script (`backup_nextcloud.sh`).<br>• Python WebDAV integration (`nextcloud_integration.py`).<br>• Project report compilation, test cases, and viva presentation slides. |

---

## 8. 🎓 Viva / Oral Examination Questions & Answers

1. **Why is Redis essential in a production Nextcloud deployment?**
   * *Answer:* Redis provides transactional file locking and in-memory caching. Without it, concurrent reads/writes cause race conditions and database deadlocks.

2. **How does Nextcloud protect against unauthorized file access?**
   * *Answer:* Through Role-Based Access Control (RBAC), server-side encryption at rest, HTTPS/TLS in transit, and file-level sharing permissions (read-only, password-protected, expiration dates).

3. **What is the advantage of using Docker Compose over manual LAMP stack installation?**
   * *Answer:* Docker Compose encapsulates dependencies, ensures identical behavior across development and cloud environments, enables one-command deployments (`docker compose up`), and isolates the database from host processes.

4. **How are file uploads handled if a user exceeds their storage quota?**
   * *Answer:* Nextcloud verifies remaining quota prior to chunk assembly. If the upload exceeds the user's allocated quota, the server returns an HTTP 507 (Insufficient Storage) error and rejects the payload.
