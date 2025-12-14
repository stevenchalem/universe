#!/usr/bin/env python3
"""
Schema subsetting for gist ontology.
Extracts topic-relevant portions for use in extraction prompts.
"""

from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode
from rdflib.namespace import SKOS, XSD
from dataclasses import dataclass, field
from typing import Optional, List, Set, Dict
import json

GIST = Namespace("https://w3id.org/semanticarts/ns/ontology/gist/")

# Topic definitions: each topic maps to seed classes
# The system will automatically include superclasses and relevant properties
TOPIC_SEEDS = {
    "organizations": [
        "Organization", "GovernmentOrganization", "CountryGovernment", 
        "SubCountryGovernment", "IntergovernmentalOrganization", "Person"
    ],
    "events": [
        "Event", "HistoricalEvent", "ContemporaryEvent", "PhysicalEvent",
        "ScheduledEvent", "Determination", "Transaction", "Task", "Project"
    ],
    "time": [
        "TimeInterval", "TemporalRelation"
    ],
    "geo": [
        "GeoLocation", "GeoPoint", "GeoRegion", "GeoVolume", "GeoRoute",
        "GovernedGeoRegion", "CountryGeoRegion", "Landmark", "Building",
        "PhysicalAddress"
    ],
    "agreements": [
        "Agreement", "Contract", "Commitment", "ContingentObligation",
        "Offer", "Account", "ContractTerm"
    ],
    "quantities": [
        "Magnitude", "Aspect", "UnitOfMeasure", "ReferenceValue",
        "SimpleUnitOfMeasure", "CoherentProductUnitOfMeasure", 
        "StandardUnitOfMeasure", "ProductUnitOfMeasure", "RatioUnitOfMeasure",
        "UnitGroup"
    ],
    "content": [
        "Content", "ContentExpression", "FormattedContent", "Message",
        "IntellectualProperty", "KnowledgeConcept", "ID", "Address",
        "ElectronicAddress"
    ],
    "collections": [
        "Collection", "OrderedCollection", "OrderedMember", "ControlledVocabulary",
        "Network", "NetworkNode", "NetworkLink"
    ],
    "categories": [
        "Category", "Tag", "Behavior", "ProductCategory", "EquipmentType",
        "MediaType", "GeneralMediaType", "Discipline"
    ],
    "artifacts": [
        "PhysicalIdentifiableItem", "Equipment", "Landmark", "Building",
        "PhysicalSubstance", "LivingThing"
    ],
    "intentions": [
        "Intention", "Requirement", "Restriction", "Permission", "Function",
        "Specification", "CatalogItem", "EventSpecification"
    ]
}

# Properties strongly associated with topics (beyond domain/range inference)
TOPIC_PROPERTIES = {
    "organizations": [
        "hasMember", "isMemberOf", "isGovernedBy", "hasJurisdictionOver",
        "isUnderJurisdictionOf", "owns", "isOwnedBy"
    ],
    "events": [
        "isParticipantIn", "hasParticipant", "isAffectedBy", "affects",
        "isTriggeredBy", "produces", "isProducedBy", "occursIn"
    ],
    "time": [
        "atDateTime", "startDateTime", "endDateTime", 
        "actualStartDateTime", "actualEndDateTime", "actualStartDate", "actualEndDate",
        "plannedStartDateTime", "plannedEndDateTime", "plannedStartDate", "plannedEndDate",
        "birthDate", "deathDate", "hasStart", "hasEnd", "hasGiver", "hasRecipient"
    ],
    "geo": [
        "hasPhysicalLocation", "isGeoContainedIn", "latitude", "longitude",
        "refersTo", "hasAddress"
    ],
    "agreements": [
        "hasParty", "hasGiver", "hasRecipient", "offersToProvide", "offersToReceive",
        "isUnderJurisdictionOf", "conformsTo"
    ],
    "quantities": [
        "hasMagnitude", "hasAspect", "hasUnitOfMeasure", "numericValue",
        "conversionFactor", "conversionOffset", "hasBaseUnit"
    ],
    "content": [
        "isExpressedIn", "isRenderedOn", "isAbout", "uniqueText", "containedText",
        "name", "description", "comesFromAgent", "goesToAgent"
    ],
    "collections": [
        "isMemberOf", "hasMember", "isDirectPartOf", "hasDirectPart",
        "precedesDirectly", "precedes", "sequence", "providesOrderFor",
        "isFirstMemberOf", "links"
    ],
    "categories": [
        "isCategorizedBy", "isAllocatedBy"
    ],
    "artifacts": [
        "isMadeUpOf", "hasBiologicalParent"
    ],
    "intentions": [
        "allows", "prevents", "requires", "conformsTo"
    ]
}


@dataclass
class ClassInfo:
    uri: str
    local_name: str
    label: Optional[str] = None
    definition: Optional[str] = None
    superclasses: List[str] = field(default_factory=list)
    subclasses: List[str] = field(default_factory=list)
    is_defined_class: bool = False

@dataclass 
class PropertyInfo:
    uri: str
    local_name: str
    label: Optional[str] = None
    definition: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    ranges: List[str] = field(default_factory=list)
    is_object_property: bool = True
    superproperties: List[str] = field(default_factory=list)
    subproperties: List[str] = field(default_factory=list)


class GistSchema:
    """Loaded gist schema with subsetting capabilities."""
    
    def __init__(self, ontology_path: str):
        self.g = Graph()
        self.g.parse(ontology_path, format="turtle")
        self.classes: Dict[str, ClassInfo] = {}
        self.properties: Dict[str, PropertyInfo] = {}
        self._extract_classes()
        self._extract_properties()
    
    def _get_local_name(self, uri):
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        return uri_str.split('/')[-1]
    
    def _get_literal(self, subject, predicate):
        for obj in self.g.objects(subject, predicate):
            return str(obj).replace('\r\n', ' ').replace('\n', ' ').strip()
        return None
    
    def _extract_classes(self):
        for cls in self.g.subjects(RDF.type, OWL.Class):
            if isinstance(cls, BNode):
                continue
            uri_str = str(cls)
            if not uri_str.startswith("https://w3id.org/semanticarts"):
                continue
            
            local = self._get_local_name(cls)
            
            info = ClassInfo(
                uri=uri_str,
                local_name=local,
                label=self._get_literal(cls, SKOS.prefLabel),
                definition=self._get_literal(cls, SKOS.definition),
            )
            
            if (cls, OWL.equivalentClass, None) in self.g:
                info.is_defined_class = True
            
            for superclass in self.g.objects(cls, RDFS.subClassOf):
                if isinstance(superclass, BNode):
                    continue
                super_str = str(superclass)
                if super_str.startswith("https://w3id.org/semanticarts"):
                    info.superclasses.append(self._get_local_name(superclass))
            
            self.classes[local] = info
        
        # Build subclass relationships
        for local, info in self.classes.items():
            for super_name in info.superclasses:
                if super_name in self.classes:
                    self.classes[super_name].subclasses.append(local)
    
    def _extract_properties(self):
        # Object properties
        for prop in self.g.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(prop, BNode):
                continue
            uri_str = str(prop)
            if not uri_str.startswith("https://w3id.org/semanticarts"):
                continue
            
            local = self._get_local_name(prop)
            
            info = PropertyInfo(
                uri=uri_str,
                local_name=local,
                label=self._get_literal(prop, SKOS.prefLabel),
                definition=self._get_literal(prop, SKOS.definition),
                is_object_property=True
            )
            
            for domain in self.g.objects(prop, RDFS.domain):
                if isinstance(domain, BNode):
                    continue
                if str(domain).startswith("https://w3id.org/semanticarts"):
                    info.domains.append(self._get_local_name(domain))
            
            for range_ in self.g.objects(prop, RDFS.range):
                if isinstance(range_, BNode):
                    continue
                if str(range_).startswith("https://w3id.org/semanticarts"):
                    info.ranges.append(self._get_local_name(range_))
            
            for superprop in self.g.objects(prop, RDFS.subPropertyOf):
                if isinstance(superprop, BNode):
                    continue
                if str(superprop).startswith("https://w3id.org/semanticarts"):
                    info.superproperties.append(self._get_local_name(superprop))
            
            self.properties[local] = info
        
        # Datatype properties
        for prop in self.g.subjects(RDF.type, OWL.DatatypeProperty):
            if isinstance(prop, BNode):
                continue
            uri_str = str(prop)
            if not uri_str.startswith("https://w3id.org/semanticarts"):
                continue
            
            local = self._get_local_name(prop)
            
            info = PropertyInfo(
                uri=uri_str,
                local_name=local,
                label=self._get_literal(prop, SKOS.prefLabel),
                definition=self._get_literal(prop, SKOS.definition),
                is_object_property=False
            )
            
            for domain in self.g.objects(prop, RDFS.domain):
                if isinstance(domain, BNode):
                    continue
                if str(domain).startswith("https://w3id.org/semanticarts"):
                    info.domains.append(self._get_local_name(domain))
            
            for range_ in self.g.objects(prop, RDFS.range):
                range_str = str(range_)
                if range_str.startswith("http://www.w3.org/2001/XMLSchema#"):
                    info.ranges.append("xsd:" + self._get_local_name(range_))
                elif not isinstance(range_, BNode):
                    info.ranges.append(self._get_local_name(range_))
            
            for superprop in self.g.objects(prop, RDFS.subPropertyOf):
                if isinstance(superprop, BNode):
                    continue
                if str(superprop).startswith("https://w3id.org/semanticarts"):
                    info.superproperties.append(self._get_local_name(superprop))
            
            self.properties[local] = info
        
        # Build subproperty relationships
        for local, info in self.properties.items():
            for super_name in info.superproperties:
                if super_name in self.properties:
                    self.properties[super_name].subproperties.append(local)
    
    def get_ancestors(self, class_name: str) -> Set[str]:
        """Get all ancestor classes."""
        ancestors = set()
        if class_name not in self.classes:
            return ancestors
        
        to_visit = list(self.classes[class_name].superclasses)
        while to_visit:
            current = to_visit.pop()
            if current in ancestors or current not in self.classes:
                continue
            ancestors.add(current)
            to_visit.extend(self.classes[current].superclasses)
        
        return ancestors
    
    def get_descendants(self, class_name: str, max_depth: int = 2) -> Set[str]:
        """Get descendant classes up to max_depth."""
        descendants = set()
        if class_name not in self.classes:
            return descendants
        
        current_level = set(self.classes[class_name].subclasses)
        for _ in range(max_depth):
            next_level = set()
            for cls in current_level:
                if cls not in descendants and cls in self.classes:
                    descendants.add(cls)
                    next_level.update(self.classes[cls].subclasses)
            current_level = next_level
        
        return descendants
    
    def get_property_ancestors(self, prop_name: str) -> Set[str]:
        """Get all ancestor properties."""
        ancestors = set()
        if prop_name not in self.properties:
            return ancestors
        
        to_visit = list(self.properties[prop_name].superproperties)
        while to_visit:
            current = to_visit.pop()
            if current in ancestors or current not in self.properties:
                continue
            ancestors.add(current)
            to_visit.extend(self.properties[current].superproperties)
        
        return ancestors
    
    def subset_by_topics(self, topics: List[str], include_descendants: bool = True) -> 'SchemaSubset':
        """
        Extract a subset of the schema relevant to the given topics.
        
        Args:
            topics: List of topic names (e.g., ["organizations", "events", "time"])
            include_descendants: Whether to include subclasses of seed classes
        
        Returns:
            SchemaSubset with selected classes and properties
        """
        selected_classes: Set[str] = set()
        selected_properties: Set[str] = set()
        
        # Gather seed classes from topics
        for topic in topics:
            if topic in TOPIC_SEEDS:
                for cls in TOPIC_SEEDS[topic]:
                    if cls in self.classes:
                        selected_classes.add(cls)
            
            # Add explicitly associated properties
            if topic in TOPIC_PROPERTIES:
                for prop in TOPIC_PROPERTIES[topic]:
                    if prop in self.properties:
                        selected_properties.add(prop)
        
        # Expand to ancestors (for hierarchy context)
        expanded_classes = set(selected_classes)
        for cls in selected_classes:
            expanded_classes.update(self.get_ancestors(cls))
        
        # Optionally include descendants
        if include_descendants:
            for cls in list(selected_classes):
                expanded_classes.update(self.get_descendants(cls, max_depth=2))
        
        selected_classes = expanded_classes
        
        # Find properties relevant to selected classes
        for prop_name, prop_info in self.properties.items():
            # Property has domain or range in our class set
            if any(d in selected_classes for d in prop_info.domains):
                selected_properties.add(prop_name)
            if prop_info.is_object_property and any(r in selected_classes for r in prop_info.ranges):
                selected_properties.add(prop_name)
        
        # Add property ancestors for hierarchy context
        expanded_properties = set(selected_properties)
        for prop in selected_properties:
            expanded_properties.update(self.get_property_ancestors(prop))
        
        return SchemaSubset(self, expanded_classes, expanded_properties)
    
    def subset_by_classes(self, class_names: List[str]) -> 'SchemaSubset':
        """
        Extract a subset containing specific classes and their relevant properties.
        """
        selected_classes: Set[str] = set()
        
        for cls in class_names:
            if cls in self.classes:
                selected_classes.add(cls)
                selected_classes.update(self.get_ancestors(cls))
        
        # Find relevant properties
        selected_properties: Set[str] = set()
        for prop_name, prop_info in self.properties.items():
            if any(d in selected_classes for d in prop_info.domains):
                selected_properties.add(prop_name)
            if prop_info.is_object_property and any(r in selected_classes for r in prop_info.ranges):
                selected_properties.add(prop_name)
        
        # Add property ancestors
        expanded_properties = set(selected_properties)
        for prop in selected_properties:
            expanded_properties.update(self.get_property_ancestors(prop))
        
        return SchemaSubset(self, selected_classes, expanded_properties)


class SchemaSubset:
    """A filtered view of the schema."""
    
    def __init__(self, schema: GistSchema, classes: Set[str], properties: Set[str]):
        self.schema = schema
        self.class_names = classes
        self.property_names = properties
    
    def to_prompt_text(self, max_definition_len: int = 120) -> str:
        """Generate LLM-friendly text representation."""
        lines = [
            "# gist Schema (subset)",
            "Prefix: gist",
            "Namespace: https://w3id.org/semanticarts/ns/ontology/gist/",
            "",
            "## Classes",
            ""
        ]
        
        # Find root classes in our subset
        roots = []
        for name in self.class_names:
            if name not in self.schema.classes:
                continue
            info = self.schema.classes[name]
            has_parent_in_subset = any(s in self.class_names for s in info.superclasses)
            if not has_parent_in_subset:
                roots.append(name)
        
        def format_class(name, indent=0, visited=None):
            if visited is None:
                visited = set()
            if name in visited or name not in self.class_names:
                return ""
            visited.add(name)
            
            info = self.schema.classes[name]
            prefix = "  " * indent
            
            marker = " [defined]" if info.is_defined_class else ""
            result = f"{prefix}gist:{name}{marker}\n"
            
            if info.definition:
                defn = info.definition[:max_definition_len]
                if len(info.definition) > max_definition_len:
                    defn += "..."
                result += f"{prefix}  {defn}\n"
            
            # Only show subclasses that are in our subset
            for sub in sorted(info.subclasses):
                if sub in self.class_names:
                    result += format_class(sub, indent + 1, visited)
            
            return result
        
        visited = set()
        for root in sorted(roots):
            lines.append(format_class(root, 0, visited))
        
        # Object properties
        obj_props = [p for p in self.property_names 
                     if p in self.schema.properties and self.schema.properties[p].is_object_property]
        if obj_props:
            lines.extend(["", "## Object Properties", ""])
            for name in sorted(obj_props):
                info = self.schema.properties[name]
                lines.append(f"gist:{name}")
                if info.definition:
                    defn = info.definition[:max_definition_len]
                    if len(info.definition) > max_definition_len:
                        defn += "..."
                    lines.append(f"  {defn}")
                constraints = []
                if info.domains:
                    constraints.append(f"Domain: {', '.join('gist:' + d for d in info.domains)}")
                if info.ranges:
                    constraints.append(f"Range: {', '.join('gist:' + r for r in info.ranges)}")
                if constraints:
                    lines.append(f"  [{'; '.join(constraints)}]")
                lines.append("")
        
        # Datatype properties
        data_props = [p for p in self.property_names 
                      if p in self.schema.properties and not self.schema.properties[p].is_object_property]
        if data_props:
            lines.extend(["## Datatype Properties", ""])
            for name in sorted(data_props):
                info = self.schema.properties[name]
                lines.append(f"gist:{name}")
                if info.definition:
                    defn = info.definition[:max_definition_len]
                    if len(info.definition) > max_definition_len:
                        defn += "..."
                    lines.append(f"  {defn}")
                constraints = []
                if info.domains:
                    constraints.append(f"Domain: {', '.join('gist:' + d for d in info.domains)}")
                if info.ranges:
                    ranges = [r if r.startswith('xsd:') else f'gist:{r}' for r in info.ranges]
                    constraints.append(f"Range: {', '.join(ranges)}")
                if constraints:
                    lines.append(f"  [{'; '.join(constraints)}]")
                lines.append("")
        
        return "\n".join(lines)
    
    def stats(self) -> dict:
        """Return statistics about this subset."""
        obj_props = sum(1 for p in self.property_names 
                        if p in self.schema.properties and self.schema.properties[p].is_object_property)
        return {
            "classes": len(self.class_names),
            "object_properties": obj_props,
            "datatype_properties": len(self.property_names) - obj_props
        }


def available_topics() -> List[str]:
    """Return list of available topic names."""
    return sorted(TOPIC_SEEDS.keys())


# Convenience function for quick access
def get_schema_for_topics(ontology_path: str, topics: List[str]) -> str:
    """
    One-liner to get schema text for given topics.
    
    Example:
        schema_text = get_schema_for_topics("gistCore.ttl", ["organizations", "events"])
    """
    schema = GistSchema(ontology_path)
    subset = schema.subset_by_topics(topics)
    return subset.to_prompt_text()


if __name__ == "__main__":
    # Demo usage
    schema = GistSchema("/mnt/user-data/uploads/gistCore14_0_0.ttl")
    
    print("Available topics:", available_topics())
    print()
    
    # Example: Get schema for articles about organizations and events
    subset = schema.subset_by_topics(["organizations", "events", "time"])
    print(f"Subset stats: {subset.stats()}")
    print()
    print("=" * 60)
    print(subset.to_prompt_text())
