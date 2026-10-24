"""
Nextcloud Cloud Storage Integration Module
Integrates the AI Resume Analyzer ML pipeline with Nextcloud via WebDAV.
Enables automated cloud resume ingestion, batch analysis, and cloud report storage.
"""

import os
import requests
from io import BytesIO

class NextcloudClient:
    """
    Connects to Nextcloud via WebDAV API to manage resume uploads,
    datasets, and candidate readiness reports.
    """
    def __init__(self, base_url=None, username=None, password=None):
        self.base_url = (base_url or os.environ.get("NEXTCLOUD_URL", "http://localhost:8080")).rstrip("/")
        self.username = username or os.environ.get("NEXTCLOUD_ADMIN_USER", "admin")
        self.password = password or os.environ.get("NEXTCLOUD_ADMIN_PASSWORD", "AdminSecurePassword2026!")
        self.webdav_url = f"{self.base_url}/remote.php/dav/files/{self.username}"
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def check_connection(self):
        """Verifies if Nextcloud server is accessible and authenticated."""
        try:
            res = self.session.request("PROPFIND", self.webdav_url, headers={"Depth": "0"})
            if res.status_code in [200, 207]:
                return True, "Successfully connected to Nextcloud server."
            return False, f"Authentication failed with HTTP {res.status_code}"
        except Exception as e:
            return False, f"Could not reach Nextcloud at {self.base_url}: {e}"

    def ensure_folder(self, folder_name):
        """Ensures a directory exists in Nextcloud storage."""
        folder_url = f"{self.webdav_url}/{folder_name.strip('/')}"
        res = self.session.request("MKCOL", folder_url)
        # 201 Created or 405 Already exists
        return res.status_code in [201, 405]

    def upload_file(self, remote_path, file_bytes):
        """Uploads a file or generated analysis report to Nextcloud."""
        target_url = f"{self.webdav_url}/{remote_path.lstrip('/')}"
        res = self.session.put(target_url, data=file_bytes)
        return res.status_code in [200, 201, 204]

    def download_resume(self, remote_filename):
        """Downloads a resume PDF from Nextcloud for ML parsing."""
        target_url = f"{self.webdav_url}/Resumes/{remote_filename.lstrip('/')}"
        res = self.session.get(target_url)
        if res.status_code == 200:
            return BytesIO(res.content)
        return None

    def list_resumes(self):
        """Lists all PDF resumes currently in the Nextcloud /Resumes folder."""
        target_url = f"{self.webdav_url}/Resumes/"
        res = self.session.request("PROPFIND", target_url, headers={"Depth": "1"})
        if res.status_code in [200, 207]:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(res.content)
            files = []
            for response in root.findall("{DAV:}response"):
                href = response.find("{DAV:}href").text
                if href.lower().endswith(".pdf"):
                    filename = href.split("/")[-1]
                    # url-decode if necessary
                    import urllib.parse
                    files.append(urllib.parse.unquote(filename))
            return files
        return []

if __name__ == "__main__":
    print("Testing Nextcloud Connection...")
    client = NextcloudClient()
    connected, msg = client.check_connection()
    print(f"Status: {connected} | {msg}")
