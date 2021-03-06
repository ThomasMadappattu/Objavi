
import tempfile

from objavi import book_utils


def render(html_path, pdf_path, **kwargs):
    """Creates a book PDF from the provided HTML document.
    """
    program = "renderer"

    params = [
        "-platform", "xcb",
        "-output", pdf_path,
    ]

    if kwargs.has_key("page_config"):
        params += ["-page-config", kwargs.get("page_config")]

    custom_css_file = None
    custom_css_text = kwargs.get("custom_css")
    if custom_css_text:
        custom_css_file = tempfile.NamedTemporaryFile(prefix="renderer-", suffix=".css", delete=True)
        custom_css_file.write(custom_css_text)
        custom_css_file.flush()
        params += ["-custom-css", custom_css_file.name]

    cmd = [ program ] + params + [ html_path ]

    try:
        book_utils.run(cmd)
    finally:
        if custom_css_file:
            custom_css_file.close()


def make_pagination_config(args):
    """Creates pagination config. text using page setting arguments.
    """
    page_settings = book_utils.get_page_settings(args)

    # NOTE: size values from page settings are always in "points"

    page_size     = page_settings.get("pointsize", (420, 595))
    top_margin    = page_settings.get("top_margin",    0.8 * 72)
    bottom_margin = page_settings.get("bottom_margin", 0.8 * 72)
    side_margin   = page_settings.get("side_margin",   0.5 * 72)
    gutter        = page_settings.get("gutter",        0.8 * 72)

    page_width, page_height = page_size

    def unit(x):
        # Convert from points (pt) to whatever is specified by lengthUnit.
        # Division by 0.75 is because of a bug currently present in the
        # renderer using pt as device pixel instead of px.
        return x / 72.0 / 0.75

    config = {
        "lengthUnit"  : "in",
        "pageWidth"   : unit(page_width),
        "pageHeight"  : unit(page_height),
        "outerMargin" : unit(side_margin),
        "innerMargin" : unit(gutter),
        "contentsTopMargin"    : unit(top_margin),
        "contentsBottomMargin" : unit(bottom_margin),
    }

    items = ["%s:%s" % (key,repr(val)) for key,val in config.items()]
    text = ",".join(items)

    return text


def make_page_settings_css(args):
    """Creates a CSS using page setting arguments.
    """
    page_settings = book_utils.get_page_settings(args)

    page_size     = page_settings.get("pointsize", (420, 595))
    top_margin    = page_settings.get("top_margin",    0.4 * 72)
    bottom_margin = page_settings.get("bottom_margin", 0.4 * 72)
    side_margin   = page_settings.get("side_margin",   0.8 * 72)
    gutter        = page_settings.get("gutter",        1.0 * 72)

    page_width, page_height = page_size

    top            = 0.8 * 72
    bottom         = 0.8 * 72
    contents_width  = page_width - side_margin - gutter
    contents_height = page_height - top - bottom

    css_text = ""

    css_text += """
.page {
    width:  %fpt;
    height: %fpt;
}
""" % (page_width, page_height)

    css_text += """
.contents {
    height: %fpt;  /* page-height - top - bottom */
    top:    %fpt;  /* top-margin + header.height */
    bottom: %fpt;  /* bottom-margin + footer.height */
}
""" % (contents_height, top, bottom)

    css_text += """
.pagenumber {
    bottom: %fpt;  /* bottom-margin */
}

.header {
    top: %fpt;     /* top-margin */
}
""" % (bottom_margin, top_margin)

    css_text += """
.page:nth-child(odd) .contents, .page:nth-child(odd) .pagenumber, .page:nth-child(odd) .header {
    left:  %fpt;   /* gutter */
    right: %fpt;   /* side-margin */
}

.page:nth-child(even) .contents, .page:nth-child(even) .pagenumber, .page:nth-child(even) .header {
    left:  %fpt;   /* side-margin */
    right: %fpt;   /* gutter */
}
""" % (gutter, side_margin, side_margin, gutter)

    css_text += """
img {
    max-width:  %fpt;  /* contents-width  * <0,1] */
    max-height: %fpt;  /* contents-height * <0,1] */
}
""" % (contents_width * 0.9, contents_height * 0.8)

    return css_text
