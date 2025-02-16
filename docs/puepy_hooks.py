from bs4 import BeautifulSoup


def on_page_content(html, page, config, files):
    soup = BeautifulSoup(html, "html.parser")
    for puepy_tag in soup.find_all("puepy"):
        src = puepy_tag.get("src", "")
        edit = puepy_tag.get("edit", "")
        height = puepy_tag.get("height", "")

        new_div = soup.new_tag(
            "div",
            **{"class": "browser", "style": f"height: {height};" if height else ""},
        )

        browser_header = soup.new_tag("div", **{"class": "browser-header"})
        browser_buttons = soup.new_tag("div", **{"class": "browser-buttons"})
        for _ in range(3):
            button = soup.new_tag("div", **{"class": "browser-button"})
            browser_buttons.append(button)
        browser_header.append(browser_buttons)

        address_bar = soup.new_tag(
            "a", **{"class": "address-bar", "target": "_blank", "href": src}
        )
        address_bar.string = src

        browser_header.append(address_bar)

        if edit:
            edit_button = soup.new_tag("a", **{"class": "edit-link", "href": edit})
            edit_button.string = "Edit"
            browser_header.append(edit_button)

        new_div.append(browser_header)

        iframe_container = soup.new_tag("div", **{"class": "iframe-container"})
        iframe = soup.new_tag("iframe", **{"class": "iframe-browser", "src": src})
        iframe_container.append(iframe)
        new_div.append(iframe_container)

        puepy_tag.replace_with(new_div)

    return str(soup)
