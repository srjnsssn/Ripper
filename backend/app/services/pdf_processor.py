import fitz


def extract_toc(file_path: str) -> list[dict]:
    doc = fitz.open(file_path)
    toc = doc.get_toc()
    total_pages = doc.page_count
    doc.close()

    chapters = []
    for level, title, page in toc:
        if level == 1:
            chapters.append({"title": title.strip(), "page": page})

    if not chapters:
        return []

    result = []
    for i, ch in enumerate(chapters):
        start = ch["page"]
        end = chapters[i + 1]["page"] - 1 if i + 1 < len(chapters) else total_pages
        result.append({
            "title": ch["title"],
            "start_page": start,
            "end_page": end,
        })

    return result
