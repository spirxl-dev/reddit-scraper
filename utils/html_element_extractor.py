import json
from bs4 import BeautifulSoup


def extract_html_elements(html_file, json_file, output_html_file, tag):
    with open(html_file, "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")

    posts = soup.find_all(tag)

    posts_content = [str(post) for post in posts]

    with open(json_file, "w") as outfile:
        json.dump(posts_content, outfile, indent=4)

    with open(output_html_file, "w") as html_outfile:
        html_outfile.write("\n".join(posts_content))

    print(
        f"Extracted {len(posts_content)} posts and saved to {json_file} and {output_html_file}"
    )


if __name__ == "__main__":
    html_file = "path_to_input_html_file"
    output_json_file = "path_to_output_json_file"
    output_html_file = "path_to_output_html_file"
    tag = "shreddit-post"
    extract_html_elements(html_file, output_json_file, output_html_file, tag)
