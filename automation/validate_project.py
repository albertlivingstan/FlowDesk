"""Validate XML, entry-point identity, references, and full BPMN DI coverage offline."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {"b": "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "d": "http://www.omg.org/spec/BPMN/20100524/DI",
      "di": "http://www.omg.org/spec/DD/20100524/DI"}


def validate() -> None:
    manifest = json.loads((ROOT / "entry-points.json").read_text())
    assert manifest["$schema"] == "https://cloud.uipath.com/draft/2024-12/entry-point"
    assert manifest["$id"] == "entry-points.json"
    entry, = manifest["entryPoints"]
    assert entry["filePath"] == "content/new.bpmn#manualTrigger1"
    assert entry["uniqueId"] == "1b957bb9-2a32-47bb-99b8-2a8d891d7d83"
    assert entry["type"] == "processorchestration"
    assert entry["displayName"] == "Email to Ticket"
    assert entry["input"]["required"] == ["emailSubject", "emailBody", "senderEmail"]
    assert entry["output"]["properties"]["status"]["enum"] == ["created", "ignored", "needs_review", "failed"]
    root = ET.parse(ROOT / "content/new.bpmn").getroot()
    all_ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
    assert len(all_ids) == len(set(all_ids)), "Duplicate BPMN IDs"
    nodes = {element.attrib["id"]: element for element in root.findall("b:process/*", NS)
             if element.tag.split("}")[-1] in {
                 "startEvent", "endEvent", "serviceTask", "userTask", "exclusiveGateway", "boundaryEvent"}}
    assert "manualTrigger1" in nodes
    flows = root.findall("b:process/b:sequenceFlow", NS)
    shapes = {shape.attrib["bpmnElement"] for shape in root.findall(".//d:BPMNShape", NS)}
    edges = {edge.attrib["bpmnElement"] for edge in root.findall(".//d:BPMNEdge", NS)}
    assert set(nodes) == shapes, "Missing BPMN node shapes"
    assert {flow.attrib["id"] for flow in flows} == edges, "Missing BPMN edge waypoints"
    for flow in flows:
        source, target = flow.attrib["sourceRef"], flow.attrib["targetRef"]
        assert source in nodes and target in nodes
        assert flow.attrib["id"] in [out.text for out in nodes[source].findall("b:outgoing", NS)]
        assert flow.attrib["id"] in [inc.text for inc in nodes[target].findall("b:incoming", NS)]
    boundary = nodes["jiraErrorBoundary"]
    assert boundary.attrib["attachedToRef"] == "createJiraTicket"
    assert boundary.find("b:errorEventDefinition", NS) is not None
    # Every model node is reachable from the preserved trigger, including error handling.
    reachable = {"manualTrigger1"}
    changed = True
    while changed:
        before = set(reachable)
        for flow in flows:
            if flow.attrib["sourceRef"] in reachable:
                reachable.add(flow.attrib["targetRef"])
        if "createJiraTicket" in reachable:
            reachable.add("jiraErrorBoundary")
        changed = before != reachable
    assert reachable == set(nodes), "Unreachable BPMN nodes"


if __name__ == "__main__":
    validate()
    print("Valid JSON and well-formed BPMN XML; identity, references, reachability and DI checked.")
