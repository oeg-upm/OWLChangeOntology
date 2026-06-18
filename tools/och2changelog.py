#!/usr/bin/env python3
"""Generate human-readable HTML or Markdown changelogs from an OCH RDF graph."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

try:
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import RDF, RDFS
except ModuleNotFoundError as exc:
    raise SystemExit("Missing dependency: install rdflib with `python3 -m pip install rdflib`.") from exc


OCH = Namespace("https://w3id.org/def/och#")

CHANGELOG_TYPES = {
    "Changelog",
    "ChangeSet",
}

ABSTRACT_TYPE_HINTS = (
    "Change",
    "Range",
    "Property",
    "Class",
    "Entity",
    "Individual",
    "Relation",
)

ENTITY_PROPERTIES = {
    "addedClass",
    "removedClass",
    "addedObjectProperty",
    "removedObjectProperty",
    "addedDataProperty",
    "removedDataProperty",
    "addedProperty",
    "removedProperty",
    "addedIndividual",
    "removedIndividual",
    "deprecatedEntity",
    "undeprecatedElement",
    "renamedEntityName",
    "outdatedEntityName",
    "addedDomainToProperty",
    "removedDomainFromProperty",
    "addedRangeToProperty",
    "removedRangeFromProperty",
    "addedCharacteristicToProperty",
    "removedCharacteristicFromProperty",
    "sourceAddSubClass",
    "sourceRemoveSubClass",
    "sourceAddSubProperty",
    "sourceRemoveSubProperty",
    "sourceAddEquivalentClass",
    "sourceRemoveEquivalentClass",
    "sourceAddEquivalentProperty",
    "sourceRemoveEquivalentProperty",
    "sourceAddDisjointClass",
    "sourceRemoveDisjointClass",
    "sourceAddDisjointProperty",
    "sourceRemoveDisjointProperty",
    "sourceAddInverseProperty",
    "sourceRemoveInverseProperty",
    "sourceAddRelationToIndividual",
    "sourceRemoveRelationToIndividual",
    "sourceAddAnnotationToEntity",
    "sourceRemoveAnnotationFromEntity",
}

DETAIL_TEMPLATES = {
    "AddClass": ("Added class", ("addedClass",)),
    "RemoveClass": ("Removed class", ("removedClass",)),
    "AddObjectProperty": ("Added object property", ("addedObjectProperty", "addedProperty")),
    "RemoveObjectProperty": ("Removed object property", ("removedObjectProperty", "removedProperty")),
    "AddDataProperty": ("Added data property", ("addedDataProperty", "addedProperty")),
    "RemoveDataProperty": ("Removed data property", ("removedDataProperty", "removedProperty")),
    "AddProperty": ("Added property", ("addedProperty",)),
    "RemoveProperty": ("Removed property", ("removedProperty",)),
    "AddIndividual": ("Added individual", ("addedIndividual",)),
    "RemoveIndividual": ("Removed individual", ("removedIndividual",)),
    "DeprecateEntity": ("Deprecated entity", ("deprecatedEntity",)),
    "RevokeDeprecate": ("Revoked deprecation", ("undeprecatedElement",)),
    "AddDomain": ("Added domain {addedDomain} to {addedDomainToProperty}", ()),
    "RemoveDomain": ("Removed domain {removedDomain} from {removedDomainFromProperty}", ()),
    "AddRange": ("Added range to {addedRangeToProperty}", ()),
    "AddRangeObjectProperty": ("Added object range {addedObjectRange} to {addedRangeToProperty}", ()),
    "AddRangeDataProperty": ("Added data range {addedDataRange} to {addedRangeToProperty}", ()),
    "RemoveRange": ("Removed range from {removedRangeFromProperty}", ()),
    "RemoveRangeObjectProperty": ("Removed object range {removedObjectRange} from {removedRangeFromProperty}", ()),
    "RemoveRangeDataProperty": ("Removed data range {removedDataRange} from {removedRangeFromProperty}", ()),
    "AddCharacteristic": ("Added characteristic {addedCharacteristic} to {addedCharacteristicToProperty}", ()),
    "RemoveCharacteristic": ("Removed characteristic {removedCharacteristic} from {removedCharacteristicFromProperty}", ()),
    "AddSubClass": ("Added subclass relation: {sourceAddSubClass} subclass of {targetAddSubClass}", ()),
    "RemoveSubClass": ("Removed subclass relation: {sourceRemoveSubClass} subclass of {targetRemoveSubClass}", ()),
    "AddSubProperty": ("Added subproperty relation: {sourceAddSubProperty} subproperty of {targetAddSubProperty}", ()),
    "AddSubPropertyOf": ("Added subproperty relation: {sourceAddSubProperty} subproperty of {targetAddSubProperty}", ()),
    "RemoveSubProperty": ("Removed subproperty relation: {sourceRemoveSubProperty} subproperty of {targetRemoveSubProperty}", ()),
    "RemoveSubPropertyOf": ("Removed subproperty relation: {sourceRemoveSubProperty} subproperty of {targetRemoveSubProperty}", ()),
    "AddEquivalentClass": ("Added equivalent classes: {sourceAddEquivalentClass} equivalent to {targetAddEquivalentClass}", ()),
    "RemoveEquivalentClass": ("Removed equivalent classes: {sourceRemoveEquivalentClass} equivalent to {targetRemoveEquivalentClass}", ()),
    "AddEquivalentProperty": ("Added equivalent properties: {sourceAddEquivalentProperty} equivalent to {targetAddEquivalentProperty}", ()),
    "RemoveEquivalentProperty": ("Removed equivalent properties: {sourceRemoveEquivalentProperty} equivalent to {targetRemoveEquivalentProperty}", ()),
    "AddDisjointClass": ("Added disjoint classes: {sourceAddDisjointClass} disjoint with {targetAddDisjointClass}", ()),
    "RemoveDisjointClass": ("Removed disjoint classes: {sourceRemoveDisjointClass} disjoint with {targetRemoveDisjointClass}", ()),
    "AddDisjointProperty": ("Added disjoint properties: {sourceAddDisjointProperty} disjoint with {targetAddDisjointProperty}", ()),
    "RemoveDisjointProperty": ("Removed disjoint properties: {sourceRemoveDisjointProperty} disjoint with {targetRemoveDisjointProperty}", ()),
    "AddInverseProperty": ("Added inverse properties: {sourceAddInverseProperty} inverse of {targetAddInverseProperty}", ()),
    "RemoveInverseProperty": ("Removed inverse properties: {sourceRemoveInverseProperty} inverse of {targetRemoveInverseProperty}", ()),
    "RenameEntity": ("Renamed entity: {outdatedEntityName} to {renamedEntityName}", ()),
    "AddRelationToIndividual": ("Added individual relation: {sourceAddRelationToIndividual} -- {addedRelationToIndividual} --> {targetAddRelationToIndividual}", ()),
    "RemoveRelationFromIndividual": ("Removed individual relation: {sourceRemoveRelationToIndividual} -- {removedRelationFromIndividual} --> {targetRemoveRelationToIndividual}", ()),
    "AddAnnotationToEntity": ("Added annotation on {sourceAddAnnotationToEntity}: {addedAnnotationToEntity} = {targetAddAnnotationToEntity}", ()),
    "RemoveAnnotationFromEntity": ("Removed annotation from {sourceRemoveAnnotationFromEntity}: {removedAnnotationFromEntity} = {targetRemoveAnnotationFromEntity}", ()),
}

CATEGORY_KEYWORDS = (
    ("Annotation", "Annotations"),
    ("Individual", "Individuals"),
    ("ObjectProperty", "Object properties"),
    ("DataProperty", "Data properties"),
    ("SubProperty", "Property relations"),
    ("EquivalentProperty", "Property relations"),
    ("DisjointProperty", "Property relations"),
    ("InverseProperty", "Property relations"),
    ("Property", "Properties"),
    ("SubClass", "Class relations"),
    ("EquivalentClass", "Class relations"),
    ("DisjointClass", "Class relations"),
    ("Class", "Classes"),
    ("Domain", "Domains"),
    ("Range", "Ranges"),
    ("Characteristic", "Property characteristics"),
    ("Rename", "Renames"),
    ("Deprecate", "Deprecations"),
    ("Entity", "Entities"),
)

PREDICATE_ALIASES = {
    "removeDomainFromProperty": "removedDomainFromProperty",
}


@dataclass
class Change:
    uri: str
    type_name: str
    type_label: str
    anchor: str
    action: str
    category: str
    entity: str
    entity_short: str
    details: list[str]
    predicates: dict[str, list[str]]


def guess_format(path: Path) -> str | None:
    suffix = path.suffix.lower()
    return {
        ".ttl": "turtle",
        ".rdf": "xml",
        ".owl": "xml",
        ".xml": "xml",
        ".nt": "nt",
        ".n3": "n3",
        ".jsonld": "json-ld",
        ".json": "json-ld",
        ".trig": "trig",
    }.get(suffix)


def local_name(value: object) -> str:
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]


def compact_uri(graph: Graph, value: URIRef) -> str:
    text = str(value)
    if text.startswith("Optional[") and text.endswith("]"):
        return compact_text(graph, text[9:-1])
    if text.startswith('"'):
        return text
    try:
        return graph.namespace_manager.normalizeUri(value)
    except Exception:
        return text


def compact_text(graph: Graph, text: str) -> str:
    if text.startswith("http://") or text.startswith("https://"):
        return compact_uri(graph, URIRef(text))
    return text


def display_value(graph: Graph, value: object) -> str:
    if isinstance(value, Literal):
        lexical = str(value).replace('\\"', '"')
        rendered = lexical if lexical.startswith('"') else value.n3(graph.namespace_manager)
    elif isinstance(value, URIRef):
        rendered = compact_uri(graph, value)
    else:
        rendered = compact_text(graph, str(value))
    return rendered.replace("\\n", "\n")


def values_for(predicates: dict[str, list[str]], key: str) -> list[str]:
    return predicates.get(key, [])


def one(predicates: dict[str, list[str]], key: str, default: str = "") -> str:
    values = values_for(predicates, key)
    return values[0] if values else default


def is_concrete_change_type(name: str) -> bool:
    if name in CHANGELOG_TYPES:
        return False
    if name.startswith(("Add", "Remove", "Rename", "Deprecate", "Revoke")):
        return True
    return not any(name.endswith(hint) for hint in ABSTRACT_TYPE_HINTS)


def choose_type(type_names: list[str]) -> str:
    concrete = [name for name in type_names if is_concrete_change_type(name)]
    if concrete:
        return sorted(concrete, key=lambda name: (len(name), name))[0]
    return sorted(type_names or ["OntologicalChange"])[0]


def classify_action(type_name: str) -> str:
    if type_name.startswith("Add"):
        return "Added"
    if type_name.startswith("Remove"):
        return "Removed"
    if type_name.startswith("Rename"):
        return "Renamed"
    if type_name.startswith("Deprecate"):
        return "Deprecated"
    if type_name.startswith("Revoke"):
        return "Restored"
    return "Changed"


def classify_category(type_name: str, predicates: dict[str, list[str]]) -> str:
    for keyword, category in CATEGORY_KEYWORDS:
        if keyword in type_name:
            return category
    predicate_names = " ".join(predicates)
    for keyword, category in CATEGORY_KEYWORDS:
        if keyword in predicate_names:
            return category
    return "Other changes"


def choose_entity(predicates: dict[str, list[str]], subject: URIRef, graph: Graph) -> tuple[str, str]:
    for key in ENTITY_PROPERTIES:
        if key in predicates and predicates[key]:
            entity = predicates[key][0]
            return entity, short_label(entity)
    subject_display = display_value(graph, subject)
    return subject_display, short_label(subject_display)


def short_label(value: str) -> str:
    text = value.strip("<>")
    if text.startswith("Optional[") and text.endswith("]"):
        text = text[9:-1]
    if text.startswith(("http://", "https://")):
        if "#" in text:
            return text.rsplit("#", 1)[1]
        return text.rstrip("/").rsplit("/", 1)[-1]
    if ":" in text and not text.startswith('"'):
        return text.rsplit(":", 1)[1]
    return text[:90] + ("..." if len(text) > 90 else "")


def render_template(template: str, predicates: dict[str, list[str]]) -> str:
    def replace(match: re.Match[str]) -> str:
        return one(predicates, match.group(1), "not specified")

    return re.sub(r"\{([^}]+)\}", replace, template)


def build_details(type_name: str, predicates: dict[str, list[str]]) -> list[str]:
    details: list[str] = []
    template = DETAIL_TEMPLATES.get(type_name)
    if template:
        text_or_label, simple_keys = template
        if simple_keys:
            for key in simple_keys:
                details.extend(f"{text_or_label}: {value}" for value in values_for(predicates, key))
        else:
            details.append(render_template(text_or_label, predicates))

    used = set()
    if template:
        used.update(re.findall(r"\{([^}]+)\}", template[0]))
        used.update(template[1])
    used.update({"fromChangelog", "issuedBy", "relatedChange", "justification"})

    for key, vals in sorted(predicates.items()):
        if key in used:
            continue
        pretty = humanize_identifier(key)
        details.extend(f"{pretty}: {value}" for value in vals)

    if "justification" in predicates:
        details.extend(f"Justification: {value}" for value in predicates["justification"])
    return details or ["Change details were not specified in the graph."]


def humanize_identifier(name: str) -> str:
    words = re.sub(r"(?<!^)([A-Z])", r" \1", name).replace("_", " ").replace("-", " ")
    return words[:1].upper() + words[1:]


def preferred_label(resource: URIRef, *graphs: Graph) -> str:
    labels: list[Literal] = []
    for graph in graphs:
        labels.extend(value for value in graph.objects(resource, RDFS.label) if isinstance(value, Literal))
    if not labels:
        return humanize_identifier(local_name(resource))
    return str(
        sorted(
            labels,
            key=lambda label: (
                0 if label.language == "en" else 1 if label.language is None else 2,
                str(label).lower(),
            ),
        )[0]
    )


def change_anchor(uri: str) -> str:
    identifier = local_name(uri.strip("<>")) or "change"
    identifier = re.sub(r"[^A-Za-z0-9_.:-]+", "-", identifier).strip("-")
    return f"change-{identifier or 'item'}"


def extract_changes(graph: Graph, vocabulary: Graph) -> list[Change]:
    subjects = set(graph.subjects(RDF.type, None))
    changes: list[Change] = []
    used_anchors: Counter[str] = Counter()

    for subject in sorted(subjects, key=str):
        type_uris = [obj for obj in graph.objects(subject, RDF.type) if str(obj).startswith(str(OCH))]
        type_names = [local_name(obj) for obj in type_uris]
        if not type_names or all(name in CHANGELOG_TYPES for name in type_names):
            continue
        type_name = choose_type(type_names)
        type_uri = next(obj for obj in type_uris if local_name(obj) == type_name)

        predicates: dict[str, list[str]] = defaultdict(list)
        for predicate, obj in graph.predicate_objects(subject):
            if predicate == RDF.type:
                continue
            key = local_name(predicate)
            predicates[key].append(display_value(graph, obj))
        for source_key, target_key in PREDICATE_ALIASES.items():
            if source_key in predicates and target_key not in predicates:
                predicates[target_key] = list(predicates[source_key])

        entity, entity_short = choose_entity(predicates, subject, graph)
        uri = display_value(graph, subject)
        base_anchor = change_anchor(uri)
        used_anchors[base_anchor] += 1
        anchor = base_anchor if used_anchors[base_anchor] == 1 else f"{base_anchor}-{used_anchors[base_anchor]}"
        changes.append(
            Change(
                uri=uri,
                type_name=type_name,
                type_label=preferred_label(type_uri, graph, vocabulary),
                anchor=anchor,
                action=classify_action(type_name),
                category=classify_category(type_name, predicates),
                entity=entity,
                entity_short=entity_short,
                details=build_details(type_name, predicates),
                predicates=dict(predicates),
            )
        )
    return changes


def find_changelog_metadata(graph: Graph, vocabulary: Graph) -> dict[str, list[str]]:
    metadata: dict[str, list[str]] = {}
    changelogs = list(graph.subjects(RDF.type, OCH.Changelog))
    if not changelogs:
        changelogs = list(graph.subjects(RDF.type, OCH.ChangeSet))
    if not changelogs:
        changelogs = list(graph.objects(None, OCH.fromChangelog))
    if not changelogs:
        return metadata

    changelog = changelogs[0]
    metadata["Changelog"] = [f"<{changelog}>" if isinstance(changelog, URIRef) else display_value(graph, changelog)]
    preferred_predicates = (OCH.prevVersion, OCH.newVersion)
    predicates = list(dict.fromkeys([*preferred_predicates, *graph.predicates(changelog, None)]))
    for predicate in predicates:
        if predicate == RDF.type:
            continue
        values = [
            f"<{obj}>" if isinstance(obj, URIRef) else display_value(graph, obj)
            for obj in graph.objects(changelog, predicate)
        ]
        if values:
            metadata[preferred_label(predicate, graph, vocabulary)] = values
    return metadata


def script_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def markdown_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("`", "\\`").replace("\n", " ")


KNOWN_NAMESPACES = {
    "och": "https://w3id.org/def/och#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "prov": "http://www.w3.org/ns/prov#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "schema": "https://schema.org/",
    "sh": "http://www.w3.org/ns/shacl#",
    "vann": "http://purl.org/vocab/vann/",
    "void": "http://rdfs.org/ns/void#",
    "cc": "http://creativecommons.org/ns#",
}


def namespace_map(*graphs: Graph) -> dict[str, str]:
    namespaces = dict(KNOWN_NAMESPACES)
    for graph in graphs:
        for prefix, namespace in graph.namespaces():
            namespaces.setdefault(prefix or "", str(namespace))
    return namespaces


LINKABLE_TERM = re.compile(
    r"<(?P<uri>https?://[^>\s]+)>|"
    r"(?<![\w/])(?P<prefix>[A-Za-z_][\w.-]*):(?P<local>[A-Za-z_](?:[\w.-]*[\w-])?)"
)


def term_uri(match: re.Match[str], namespaces: dict[str, str]) -> str | None:
    if match.group("uri"):
        return match.group("uri")
    namespace = namespaces.get(match.group("prefix"))
    return f"{namespace}{match.group('local')}" if namespace else None


def compact_uri_label(uri: str, namespaces: dict[str, str]) -> str:
    matches = [
        (prefix, namespace)
        for prefix, namespace in namespaces.items()
        if prefix and uri.startswith(namespace) and uri != namespace
    ]
    if not matches:
        return f"<{uri}>"
    prefix, namespace = min(
        matches,
        key=lambda item: (
            -len(item[1]),
            0 if item[0] in KNOWN_NAMESPACES else 1,
            len(item[0]),
            item[0],
        ),
    )
    return f"{prefix}:{uri[len(namespace):]}"


def markdown_link(label: str, target: str, namespaces: dict[str, str]) -> str:
    clean_target = target.strip("<>")
    rendered_label = compact_uri_label(clean_target, namespaces) if clean_target.startswith(("http://", "https://")) else label
    clean_label = markdown_text(rendered_label)
    if clean_target.startswith(("http://", "https://")):
        return f"[{clean_label}]({clean_target.replace(' ', '%20')})"
    compact_match = LINKABLE_TERM.fullmatch(clean_target)
    resolved = term_uri(compact_match, namespaces) if compact_match else None
    if resolved:
        return f"[{clean_label}]({resolved})"
    return f"`{clean_label}`"


def linkify_markdown(value: str, namespaces: dict[str, str]) -> str:
    parts: list[str] = []
    cursor = 0
    for match in LINKABLE_TERM.finditer(value):
        parts.append(markdown_text(value[cursor : match.start()]))
        target = term_uri(match, namespaces)
        label = compact_uri_label(target, namespaces) if match.group("uri") and target else match.group(0)
        parts.append(f"[{markdown_text(label)}]({target})" if target else markdown_text(label))
        cursor = match.end()
    parts.append(markdown_text(value[cursor:]))
    return "".join(parts)


def render_markdown(
    changes: list[Change],
    metadata: dict[str, list[str]],
    title: str,
    source: Path,
    namespaces: dict[str, str],
) -> str:
    action_order = ("Added", "Removed", "Changed", "Renamed", "Deprecated", "Restored")
    grouped: dict[str, dict[str, list[Change]]] = defaultdict(lambda: defaultdict(list))
    for change in changes:
        grouped[change.action][change.category].append(change)

    lines = [
        f"# {markdown_text(title)}",
        "",
        f"> Generated from `{markdown_text(str(source))}`. **{len(changes)} ontological changes.**",
        "",
    ]

    if metadata:
        lines.extend(["## Changelog metadata", ""])
        for key, values in metadata.items():
            rendered_values = ", ".join(markdown_link(value, value, namespaces) for value in values)
            lines.append(f"- **{markdown_text(key)}:** {rendered_values}")
        lines.append("")

    ordered_actions = [action for action in action_order if action in grouped]
    ordered_actions.extend(sorted(set(grouped) - set(ordered_actions)))

    for action in ordered_actions:
        action_changes = sum(len(items) for items in grouped[action].values())
        lines.extend([f"## {action} ({action_changes})", ""])
        for category, items in sorted(grouped[action].items()):
            lines.extend([f"### {markdown_text(category)}", ""])
            for change in sorted(items, key=lambda c: (c.entity_short.lower(), c.type_name, c.uri)):
                entity = markdown_link(change.entity_short, change.entity, namespaces)
                lines.append(
                    f"- <a id=\"{change.anchor}\"></a>**{entity}** "
                    f"`{markdown_text(change.type_label)}` "
                    f"[permalink](#{change.anchor})"
                )
                for detail in change.details:
                    lines.append(f"  - {linkify_markdown(detail, namespaces)}")
            lines.append("")

    if not changes:
        lines.extend(["## Changes", "", "_No ontological changes were found._", ""])

    lines.extend(
        [
            "---",
            "",
            "Generated by `tools/och_changelog_html.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def html_link(
    value: str,
    namespaces: dict[str, str],
    label: str | None = None,
    class_name: str | None = None,
) -> str:
    target = value.strip("<>")
    rendered_label = label if label is not None else (
        compact_uri_label(target, namespaces) if target.startswith(("http://", "https://")) else value
    )
    class_attribute = f' class="{escape(class_name)}"' if class_name else ""
    if target.startswith(("http://", "https://")):
        return f'<a{class_attribute} href="{escape(target)}">{escape(rendered_label)}</a>'
    compact_match = LINKABLE_TERM.fullmatch(target)
    resolved = term_uri(compact_match, namespaces) if compact_match else None
    if resolved:
        return f'<a{class_attribute} href="{escape(resolved)}">{escape(rendered_label)}</a>'
    return escape(rendered_label)


def linkify_html(value: str, namespaces: dict[str, str]) -> str:
    parts: list[str] = []
    cursor = 0
    for match in LINKABLE_TERM.finditer(value):
        parts.append(escape(value[cursor : match.start()]))
        target = term_uri(match, namespaces)
        label = compact_uri_label(target, namespaces) if match.group("uri") and target else match.group(0)
        parts.append(f'<a href="{escape(target)}">{escape(label)}</a>' if target else escape(label))
        cursor = match.end()
    parts.append(escape(value[cursor:]))
    return "".join(parts)


def render_html(
    changes: list[Change],
    metadata: dict[str, list[str]],
    title: str,
    source: Path,
    namespaces: dict[str, str],
) -> str:
    category_counts = Counter(change.category for change in changes)
    action_counts = Counter(change.action for change in changes)
    type_counts = Counter((change.type_name, change.type_label) for change in changes)
    groups: dict[str, list[Change]] = defaultdict(list)
    for change in changes:
        groups[change.category].append(change)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    change_json = [
        {
            "id": index,
            "query": " ".join(
                [c.uri, c.type_name, c.type_label, c.action, c.category, c.entity, c.entity_short, *c.details]
            ).lower(),
            "category": c.category,
            "action": c.action,
            "type": c.type_name,
            "typeLabel": c.type_label,
        }
        for index, c in enumerate(changes)
    ]
    change_ids = {change.uri: index for index, change in enumerate(changes)}

    stat_cards = "\n".join(
        f'<div class="stat"><span>{escape(str(value))}</span><strong>{escape(label)}</strong></div>'
        for label, value in (
            ("changes", len(changes)),
            ("categories", len(category_counts)),
            ("change types", len(type_counts)),
            ("generated", generated_at.split()[0]),
        )
    )

    if metadata:
        meta_html = "".join(
            f"<div><dt>{escape(key)}</dt><dd>{', '.join(html_link(value, namespaces) for value in values)}</dd></div>"
            for key, values in metadata.items()
        )
        serialization_note = "Human-readable HTML serialization of the OCH changelog."
    else:
        meta_html = (
            "<div><dt>Changelog metadata</dt>"
            "<dd>No changelog resource or version metadata is provided in this RDF graph.</dd></div>"
        )
        serialization_note = "Human-readable HTML serialization of an OCH change graph."

    action_options = "\n".join(
        f'<option value="{escape(action)}">{escape(action)} ({count})</option>'
        for action, count in sorted(action_counts.items())
    )
    category_options = "\n".join(
        f'<option value="{escape(category)}">{escape(category)} ({count})</option>'
        for category, count in sorted(category_counts.items())
    )
    type_options = "\n".join(
        f'<option value="{escape(type_name)}">{escape(type_label)} ({count})</option>'
        for (type_name, type_label), count in sorted(type_counts.items(), key=lambda item: item[0][1].lower())
    )

    group_html = []
    for category, items in sorted(groups.items()):
        cards = []
        for change in sorted(items, key=lambda c: (c.entity_short.lower(), c.type_name, c.uri)):
            change_id = change_ids[change.uri]
            detail_items = "\n".join(f"<li>{linkify_html(detail, namespaces)}</li>" for detail in change.details)
            predicate_rows = "\n".join(
                f"<tr><th>{escape(humanize_identifier(key))}</th>"
                f"<td>{', '.join(linkify_html(value, namespaces) for value in vals)}</td></tr>"
                for key, vals in sorted(change.predicates.items())
            )
            cards.append(
                f"""
                <article id="{escape(change.anchor)}" class="change-card" data-id="{change_id}">
                  <header>
                    <div>
                      <p class="eyebrow">{escape(change.action)} / {escape(change.type_label)}</p>
                      <h3>{escape(change.entity_short)}</h3>
                    </div>
                    <div class="card-links">
                      <a class="permalink" href="#{escape(change.anchor)}" title="Permanent link to this change">
                        #{escape(change.anchor.removeprefix("change-"))}
                      </a>
                      {html_link(change.entity, namespaces, class_name="uri")}
                    </div>
                  </header>
                  <ul class="details">{detail_items}</ul>
                  <details class="raw">
                    <summary>RDF properties</summary>
                    <table>{predicate_rows}</table>
                    <p class="change-uri">Change URI: {html_link(change.uri, namespaces)}</p>
                  </details>
                </article>
                """
            )
        group_html.append(
            f"""
            <section class="category-group" data-category="{escape(category)}">
              <div class="group-heading">
                <h2>{escape(category)}</h2>
                <span>{len(items)} changes</span>
              </div>
              <div class="cards">
                {''.join(cards)}
              </div>
            </section>
            """
        )

    empty_state = """
      <div id="emptyState" class="empty" hidden>
        <h2>No changes match the current filters</h2>
        <p>Try a broader search term or clear one of the filters.</p>
      </div>
    """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #182026;
      --muted: #65717a;
      --line: #d9e0e5;
      --panel: #ffffff;
      --page: #f6f8f9;
      --accent: #176b87;
      --accent-2: #7a4f1d;
      --added: #0f7b4f;
      --removed: #b33f32;
      --focus: #0b5fff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    .shell {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 52px; }}
    .hero {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 22px; align-items: end; margin-bottom: 22px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.6rem); letter-spacing: 0; line-height: 1; }}
    .subtitle {{ max-width: 760px; margin: 0; color: var(--muted); font-size: 1rem; overflow-wrap: anywhere; }}
    .stats {{ display: grid; grid-template-columns: repeat(2, minmax(120px, 1fr)); gap: 10px; }}
    .stat {{ min-width: 128px; border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 12px; }}
    .stat span {{ display: block; color: var(--accent); font-size: 1.35rem; font-weight: 750; }}
    .stat strong {{ display: block; color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; }}
    .metadata {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin: 18px 0 22px; }}
    .metadata div {{ border-left: 3px solid var(--accent-2); background: #fffaf3; padding: 10px 12px; }}
    dt {{ color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; }}
    dd {{ margin: 2px 0 0; overflow-wrap: anywhere; }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      grid-template-columns: minmax(240px, 1fr) repeat(3, minmax(150px, 190px));
      gap: 10px;
      align-items: center;
      padding: 12px;
      margin: 0 0 22px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, .96);
      backdrop-filter: blur(10px);
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(24, 32, 38, .08);
    }}
    input, select, button {{
      width: 100%;
      min-height: 42px;
      border: 1px solid #c9d3da;
      border-radius: 6px;
      background: white;
      color: var(--ink);
      font: inherit;
      padding: 0 12px;
    }}
    button {{ cursor: pointer; background: var(--ink); color: white; border-color: var(--ink); }}
    input:focus, select:focus, button:focus {{ outline: 3px solid color-mix(in srgb, var(--focus) 24%, transparent); outline-offset: 1px; }}
    .group-heading {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin: 24px 0 10px; }}
    .group-heading h2 {{ margin: 0; font-size: 1.25rem; }}
    .group-heading span {{ color: var(--muted); white-space: nowrap; }}
    .cards {{ display: grid; gap: 10px; }}
    .change-card {{
      scroll-margin-top: 88px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 15px;
      box-shadow: 0 1px 0 rgba(24, 32, 38, .04);
    }}
    .change-card:target {{ border-color: var(--focus); box-shadow: 0 0 0 3px color-mix(in srgb, var(--focus) 16%, transparent); }}
    .change-card[hidden], .category-group[hidden] {{ display: none; }}
    .change-card header {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(190px, 34%); gap: 14px; align-items: start; }}
    .eyebrow {{ margin: 0 0 3px; color: var(--accent); font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }}
    h3 {{ margin: 0; font-size: 1.08rem; overflow-wrap: anywhere; }}
    .card-links {{ display: grid; justify-items: end; gap: 4px; min-width: 0; }}
    .permalink {{ color: var(--accent); font-size: .82rem; font-weight: 700; text-decoration: none; }}
    .permalink:hover {{ text-decoration: underline; }}
    .uri {{ color: var(--muted); font-size: .86rem; text-align: right; overflow-wrap: anywhere; text-decoration-color: #b9c4cb; }}
    .details {{ margin: 12px 0 0; padding-left: 20px; }}
    .details li {{ margin: 4px 0; overflow-wrap: anywhere; }}
    .details a, .raw td a, .metadata a, .change-uri a {{
      color: inherit;
      text-decoration-line: underline;
      text-decoration-style: dotted;
      text-decoration-color: #91a3ad;
      text-underline-offset: 3px;
    }}
    .details a:visited, .raw td a:visited, .metadata a:visited, .change-uri a:visited {{ color: inherit; }}
    .details a:hover, .raw td a:hover, .metadata a:hover, .change-uri a:hover {{
      color: var(--accent);
      text-decoration-style: solid;
    }}
    .raw {{ margin-top: 10px; color: var(--muted); }}
    .raw summary {{ cursor: pointer; font-size: .9rem; }}
    table {{ width: 100%; margin-top: 8px; border-collapse: collapse; font-size: .9rem; }}
    th, td {{ border-top: 1px solid var(--line); padding: 7px 4px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ width: 220px; color: var(--muted); font-weight: 650; }}
    .change-uri {{ margin: 8px 0 0; overflow-wrap: anywhere; font-size: .86rem; }}
    .empty {{ border: 1px dashed #b6c0c7; border-radius: 8px; padding: 28px; text-align: center; background: white; }}
    .empty h2 {{ margin: 0 0 6px; }}
    .empty p {{ margin: 0; color: var(--muted); }}
    .footer {{ margin-top: 26px; color: var(--muted); font-size: .86rem; }}
    @media (max-width: 860px) {{
      .hero, .toolbar, .change-card header {{ grid-template-columns: 1fr; }}
      .card-links {{ justify-items: start; }}
      .uri {{ text-align: left; }}
      .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <h1>{escape(title)}</h1>
        <p class="subtitle">{escape(serialization_note)}</p>
      </div>
      <div class="stats">{stat_cards}</div>
    </section>
    <dl class="metadata">{meta_html}</dl>
    <form class="toolbar" role="search">
      <input id="searchInput" type="search" placeholder="Search entities, IRIs, annotations, types..." autocomplete="off">
      <select id="categoryFilter" aria-label="Category">
        <option value="">All categories</option>
        {category_options}
      </select>
      <select id="actionFilter" aria-label="Action">
        <option value="">All actions</option>
        {action_options}
      </select>
      <select id="typeFilter" aria-label="Change type">
        <option value="">All types</option>
        {type_options}
      </select>
    </form>
    <div id="resultCount" class="footer">{len(changes)} visible changes</div>
    {''.join(group_html)}
    {empty_state}
    <p class="footer">Generated by tools/och_changelog_html.py on {escape(generated_at)}.</p>
  </main>
  <script>
    const changes = {script_json(change_json)};
    const controls = {{
      search: document.getElementById('searchInput'),
      category: document.getElementById('categoryFilter'),
      action: document.getElementById('actionFilter'),
      type: document.getElementById('typeFilter')
    }};
    const resultCount = document.getElementById('resultCount');
    const emptyState = document.getElementById('emptyState');

    function matches(change, filters, excluded = '') {{
      return (!filters.search || change.query.includes(filters.search))
        && (excluded === 'category' || !filters.category || change.category === filters.category)
        && (excluded === 'action' || !filters.action || change.action === filters.action)
        && (excluded === 'type' || !filters.type || change.type === filters.type);
    }}

    function currentFilters() {{
      return {{
        search: controls.search.value.trim().toLowerCase(),
        category: controls.category.value,
        action: controls.action.value,
        type: controls.type.value
      }};
    }}

    function availableValues(field, filters) {{
      const values = new Map();
      for (const change of changes) {{
        if (!matches(change, filters, field)) continue;
        const value = change[field];
        const label = field === 'type' ? change.typeLabel : value;
        const entry = values.get(value) || {{ label, count: 0 }};
        entry.count++;
        values.set(value, entry);
      }}
      return values;
    }}

    function normalizeSelections(filters) {{
      let changed = true;
      while (changed) {{
        changed = false;
        for (const field of ['category', 'action', 'type']) {{
          if (filters[field] && !availableValues(field, filters).has(filters[field])) {{
            filters[field] = '';
            controls[field].value = '';
            changed = true;
          }}
        }}
      }}
    }}

    function updateSelect(field, filters) {{
      const select = controls[field];
      const selected = filters[field];
      const values = availableValues(field, filters);
      const labels = {{
        category: 'All categories',
        action: 'All actions',
        type: 'All types'
      }};
      const options = [...values.entries()].sort((left, right) =>
        left[1].label.localeCompare(right[1].label)
      );

      select.replaceChildren(new Option(labels[field], ''));
      for (const [value, item] of options) {{
        select.add(new Option(`${{item.label}} (${{item.count}})`, value));
      }}
      select.value = values.has(selected) ? selected : '';
    }}

    function applyFilters() {{
      const filters = currentFilters();
      normalizeSelections(filters);
      updateSelect('category', filters);
      updateSelect('action', filters);
      updateSelect('type', filters);
      let visible = 0;

      for (const change of changes) {{
        const match = matches(change, filters);
        const card = document.querySelector(`[data-id="${{change.id}}"]`);
        card.hidden = !match;
        if (match) visible++;
      }}

      for (const group of document.querySelectorAll('.category-group')) {{
        group.hidden = group.querySelectorAll('.change-card:not([hidden])').length === 0;
      }}
      resultCount.textContent = `${{visible}} visible change${{visible === 1 ? '' : 's'}}`;
      emptyState.hidden = visible !== 0;
    }}

    Object.values(controls).forEach(control => control.addEventListener('input', applyFilters));
    applyFilters();
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an HTML or Markdown changelog from an RDF graph using the OCH vocabulary."
    )
    parser.add_argument("input", type=Path, help="Input RDF graph (.ttl, .rdf, .owl, .nt, .jsonld, ...)")
    parser.add_argument("-o", "--output", type=Path, help="Output .html or .md file")
    parser.add_argument("--title", default="Ontological changelog", help="Changelog title")
    parser.add_argument(
        "--output-format",
        choices=("html", "markdown", "md"),
        help="Output format; inferred from --output when omitted (default: html)",
    )
    parser.add_argument("--format", dest="rdf_format", help="rdflib parser format override")
    return parser.parse_args()


def choose_output_format(requested: str | None, output: Path | None) -> str:
    if requested:
        return "markdown" if requested == "md" else requested
    if output and output.suffix.lower() in {".md", ".markdown"}:
        return "markdown"
    return "html"


def load_vocabulary() -> Graph:
    vocabulary = Graph()
    ontology_path = Path(__file__).resolve().parent.parent / "ontology" / "och_ontology_3.0.ttl"
    if ontology_path.exists():
        vocabulary.parse(ontology_path, format="turtle")
    return vocabulary


def main() -> int:
    args = parse_args()
    source = args.input
    output_format = choose_output_format(args.output_format, args.output)
    output = args.output or source.with_suffix(".md" if output_format == "markdown" else ".html")

    graph = Graph()
    rdf_format = args.rdf_format or guess_format(source)
    graph.parse(source, format=rdf_format)
    vocabulary = load_vocabulary()
    namespaces = namespace_map(vocabulary, graph)

    changes = extract_changes(graph, vocabulary)
    metadata = find_changelog_metadata(graph, vocabulary)
    content = (
        render_markdown(changes, metadata, args.title, source, namespaces)
        if output_format == "markdown"
        else render_html(changes, metadata, args.title, source, namespaces)
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote {output} ({output_format}) with {len(changes)} changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
