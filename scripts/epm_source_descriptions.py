"""The editorial substitution for the shared release's customer source title.

Keep this substitution exact: the viewer uses it to check a cut against its pinned
release. It must never authorize a change to another source, term or relationship.
"""

OLD_TITLE = (
    "the subject matter expert's customer inputs of 2026-10-27 "
    "(two images and two Dealer Master documents), as the party module holds them"
)
NEW_TITLE = (
    "the subject matter expert's customer inputs of 2026-10-27 "
    "(including two Dealer Master documents), "
    "as the party module holds them"
)


def neutral_source_description(text):
    return text.replace(OLD_TITLE, NEW_TITLE)
