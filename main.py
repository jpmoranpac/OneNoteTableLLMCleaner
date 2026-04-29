import tableExtractor
import poc

if __name__ == "__main__":
    headings, parsed = tableExtractor.parse_onenote_csv("input.csv")
    
    for row in parsed:
        for text in row["Presentation"]:
            corrected = poc.proofread_text(text)
            row["Presentation"] = corrected

    print(parsed)
    
    matrix = tableExtractor.to_matrix(headings, parsed)

    for row in matrix:
        print(row)

    tableExtractor.export_to_html(matrix, "conference_notes.html")