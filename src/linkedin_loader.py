import os
import zipfile
from pathlib import Path
from typing import Optional
import pandas as pd
from langchain.schema import Document


LINKEDIN_FILES = {
    "Profile.csv": "profile",
    "Positions.csv": "experience",
    "Education.csv": "education",
    "Skills.csv": "skills",
    "Connections.csv": "connections",
    "Certifications.csv": "certifications",
    "Languages.csv": "languages",
    "Projects.csv": "projects",
    "Recommendations_Received.csv": "recommendations",
}


def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(str(path), skiprows=0, encoding="utf-8", on_bad_lines="skip")
        if df.empty:
            return None
        return df
    except Exception:
        try:
            df = pd.read_csv(str(path), skiprows=1, encoding="utf-8", on_bad_lines="skip")
            return df if not df.empty else None
        except Exception:
            return None


def _extract_zip(zip_path: str, extract_to: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
    return extract_to


def _build_profile_text(df: pd.DataFrame) -> str:
    row = df.iloc[0]
    parts = ["LinkedIn Profile:"]
    for col in df.columns:
        val = row.get(col, "")
        if pd.notna(val) and str(val).strip():
            parts.append(f"  {col}: {val}")
    return "\n".join(parts)


def _build_experience_text(df: pd.DataFrame) -> str:
    parts = ["Work Experience (from LinkedIn):"]
    for _, row in df.iterrows():
        title = row.get("Title", row.get("Position Title", ""))
        company = row.get("Company Name", row.get("Company", ""))
        start = row.get("Started On", row.get("Start Date", ""))
        end = row.get("Finished On", row.get("End Date", "Currently Working"))
        description = row.get("Description", "")

        entry = f"\n  - {title} at {company}"
        if start:
            entry += f" ({start} -> {end if pd.notna(end) else 'Present'})"
        if pd.notna(description) and str(description).strip():
            entry += f"\n    {description}"
        parts.append(entry)
    return "\n".join(parts)


def _build_education_text(df: pd.DataFrame) -> str:
    parts = ["Education (from LinkedIn):"]
    for _, row in df.iterrows():
        school = row.get("School Name", row.get("School", ""))
        degree = row.get("Degree Name", row.get("Degree", ""))
        field = row.get("Field Of Study", "")
        start = row.get("Start Date", "")
        end = row.get("End Date", "")

        entry = f"\n  - {degree} in {field}" if field else f"\n  - {degree}"
        entry += f" at {school}"
        if start:
            entry += f" ({start} -> {end if pd.notna(end) else 'Present'})"
        parts.append(entry)
    return "\n".join(parts)


def _build_skills_text(df: pd.DataFrame) -> str:
    skills = []
    for _, row in df.iterrows():
        skill = row.get("Name", row.get("Skill", ""))
        if pd.notna(skill) and str(skill).strip():
            skills.append(str(skill).strip())
    return f"Skills (from LinkedIn):\n  {', '.join(skills)}"


def _build_generic_text(df: pd.DataFrame, section_name: str) -> str:
    parts = [f"{section_name} (from LinkedIn):"]
    for _, row in df.iterrows():
        row_text = " | ".join(
            f"{col}: {val}"
            for col, val in row.items()
            if pd.notna(val) and str(val).strip()
        )
        if row_text:
            parts.append(f"  - {row_text}")
    return "\n".join(parts)


def load_linkedin(csv_path: str) -> list:
    path = Path(csv_path)
    documents = []

    if not path.exists():
        print(
            f"Warning: LinkedIn file not found at: {csv_path}\n"
            f"Download your export from LinkedIn and place it at: data/linkedin_export.zip\n"
            f"Skipping LinkedIn for now."
        )
        return []

    if path.suffix.lower() == ".zip":
        extract_dir = path.parent / "linkedin_extracted"
        extract_dir.mkdir(exist_ok=True)
        _extract_zip(str(path), str(extract_dir))
        search_dir = extract_dir
    elif path.is_dir():
        search_dir = path
    else:
        search_dir = path.parent

    found_count = 0
    for filename, section_type in LINKEDIN_FILES.items():
        file_path = search_dir / filename
        if not file_path.exists():
            continue

        df = _safe_read_csv(file_path)
        if df is None:
            continue

        try:
            if section_type == "profile":
                text = _build_profile_text(df)
            elif section_type == "experience":
                text = _build_experience_text(df)
            elif section_type == "education":
                text = _build_education_text(df)
            elif section_type == "skills":
                text = _build_skills_text(df)
            else:
                text = _build_generic_text(df, section_type.capitalize())

            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": "LinkedIn", "type": section_type, "file": filename},
                )
            )
            found_count += 1
        except Exception as e:
            print(f"  Warning: Could not read {filename}: {e}")

    if found_count == 0:
        print("Warning: No known LinkedIn files found in export")
    else:
        print(f"LinkedIn: Loaded {found_count} file(s) from export")

    return documents