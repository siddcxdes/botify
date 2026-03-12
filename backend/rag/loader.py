"""
Document loading and chunking utilities.
"""

import os
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

DOCS_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

# Fallback content used when no PDFs are present in a domain folder.
FALLBACK_CONTENT = {
    "lawfirm": (
        "Smith & Associates is a full-service law firm established in 2003 with over "
        "20 experienced attorneys. We specialize in corporate law, family law, criminal "
        "defense, intellectual property, and contract disputes. Our firm has successfully "
        "handled 5,000+ cases with a 94% client satisfaction rate. We offer free initial "
        "consultations for all new clients. Office hours are Monday to Friday, 9 AM to "
        "6 PM. We are located at 45 Justice Avenue, Downtown Business District. Our "
        "senior partners include Adv. Raghav Mehta (Corporate Law), Adv. Priya Sharma "
        "(Family Law), and Adv. Karan Singh (Criminal Defense). We also provide legal "
        "document drafting, mediation services, and representation in high courts. "
        "Our retainer packages start at INR 25,000 per month for small businesses. "
        "Contact us at legal@smithassociates.com or call +91-98765-43210."
    ),
    "realestate": (
        "GreenNest Realty is a premium real estate agency operating since 2010 across "
        "multiple cities. We currently have 150+ active property listings ranging from "
        "affordable 1BHK apartments starting at 15 lakhs to luxury 4BHK villas up to "
        "3 crore. Our 3BHK options in the east zone start from 55 lakhs and in the west "
        "zone from 65 lakhs, most with covered parking and society amenities. We handle "
        "buying, selling, renting, and commercial leasing. Virtual tours are available "
        "for all premium listings. Our agents are available 7 days a week from 9 AM to "
        "8 PM. We also assist with home loans through our banking partners with interest "
        "rates starting at 8.5%. Office located at 12 Skyline Tower, MG Road. "
        "Top localities we cover: Whitefield, Koramangala, Baner, Hinjewadi, and Powai. "
        "Contact us at hello@greennestrealty.com or call +91-99887-66554."
    ),
    "dental": (
        "BrightSmile Dental Clinic is a state-of-the-art dental care facility "
        "established in 2015. We offer a comprehensive range of treatments including "
        "teeth whitening (starting at INR 2,500 per session), dental braces (starting "
        "at INR 25,000), root canal therapy (INR 3,000–8,000 per tooth), dental implants "
        "(INR 20,000–50,000), cosmetic veneers, teeth cleaning and scaling (INR 800), "
        "and pediatric dentistry. Our LED whitening sessions show visible results in a "
        "single sitting. We also offer monthly whitening maintenance packages. The clinic "
        "is open Monday to Saturday, 10 AM to 8 PM, and Sundays by appointment only. "
        "We have 5 experienced dentists led by Dr. Ananya Reddy (MDS, Cosmetic Dentistry) "
        "and Dr. Vikram Joshi (MDS, Orthodontics). Free first consultation for all new "
        "patients. Located at 78 Wellness Plaza, Health Hub Road. "
        "Book online at brightsmileclinic.com or call +91-88776-55443."
    ),
}


def load_documents(domain: str) -> list[Document]:
    """
    Load PDF documents from the domain folder.
    Falls back to hardcoded content if the folder is empty.
    """
    domain_path = os.path.join(DOCS_ROOT, domain)
    os.makedirs(domain_path, exist_ok=True)

    # Check for document files
    pdf_files = [f for f in os.listdir(domain_path) if f.lower().endswith(".pdf")]
    txt_files = [f for f in os.listdir(domain_path) if f.lower().endswith(".txt")]

    raw_docs = []

    if pdf_files:
        loader = PyPDFDirectoryLoader(domain_path)
        raw_docs.extend(loader.load())

    if txt_files:
        txt_loader = DirectoryLoader(
            domain_path, glob="**/*.txt", loader_cls=TextLoader
        )
        raw_docs.extend(txt_loader.load())

    if not raw_docs:
        # Use fallback content
        raw_docs = [
            Document(
                page_content=FALLBACK_CONTENT[domain],
                metadata={"source": f"fallback-{domain}", "domain": domain},
            )
        ]

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)
    return chunks
