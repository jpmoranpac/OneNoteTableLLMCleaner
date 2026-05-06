import tableExtractor
import poc

if __name__ == "__main__":
    headings, parsed = tableExtractor.parse_onenote_csv("DDC-utf8.csv")
    
    print("Parsing via LLM", end="")
    for row in parsed:
        for text in row["Presentation"]:
            corrected = poc.proofread_text(text)
            row["Presentation"] = corrected
            print(".", end="", flush=True)

    #print(parsed)
    
    print("LLM Processing complete! Now writing to htmml...")

    matrix = tableExtractor.to_matrix(headings, parsed)

    #for row in matrix:
    #    print(row)

    tableExtractor.export_to_html(matrix, "conference_notes.html")

    print("HTML writing complete! See conference_notes.html")