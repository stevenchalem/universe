# gist Core Ontology - LLM Reference
Version: 14.0.0
Prefix: gist
Namespace: https://w3id.org/semanticarts/ns/ontology/gist/

## Overview

gist is a minimalist upper ontology for enterprise systems. Use it as a 
foundation for domain modeling—attach your domain classes as subclasses 
of gist classes, and use gist properties where they fit.

## Key Modeling Patterns

### Magnitudes (Quantities)
To represent a measured value:
- Create a gist:Magnitude instance
- Link it with gist:hasAspect to what's being measured (e.g., mass, duration)
- Link it with gist:hasUnitOfMeasure to the unit
- Set gist:numericValue to the actual number

### Temporal Information
Events use datetime properties:
- gist:plannedStartDateTime / gist:plannedEndDateTime - scheduled times
- gist:actualStartDateTime / gist:actualEndDateTime - when it actually happened
- Precision variants: ...Date (day), ...Minute, ...Year

### Organizations and People
- gist:Organization - companies, agencies, teams
- gist:Person - individual humans
- gist:hasMember - membership relationships
- gist:isGovernedBy - governance/authority relationships

### Agreements and Commitments  
- gist:Agreement - mutual arrangement between parties
- gist:Commitment - unilateral promise by one party
- gist:Contract - legally enforceable agreement
- gist:hasParty, gist:hasGiver, gist:hasRecipient - party relationships

### Geographic
- gist:GeoPoint - lat/long/altitude
- gist:GeoRegion - bounded area
- gist:GeoLocation - general physical location
- gist:hasPhysicalLocation - links things to places

### Categories vs Classes
Use gist:Category and gist:isCategorizedBy for lightweight tagging that 
doesn't need formal semantics. Use owl:Class subclassing for formal types.

---

## Class Hierarchy

Legend: [defined] = has equivalentClass axiom (necessary & sufficient conditions)

gist:Account [defined]
  An agreement having a balance.
gist:Agreement [defined]
  A mutually understood arrangement in which two or more parties make commitments to one another.
gist:Aspect
  A measurable characteristic.
gist:Assignment [defined]
  A temporal relationship between an assignee, the thing assigned, and the resource that made the assignment.
gist:BundledCatalogItem [defined]
  Any combination of descriptions of things offered together.
gist:Category
  A concept or label used to categorize other instances without specifying any formal semantics.
  gist:AddressUsageType
    A category indicating the context or manner in which an address may be used.
  gist:Behavior
    A category indicating the nature of an activity.
  gist:DegreeOfCommitment
    The difficulty of reversing a commitment.
  gist:Discipline
    An area of study or practice.
  gist:ElectronicAddressType
    A category indicating a kind of electronic address. Such a category is usually based on the technology that enables routing to the address referent.
  gist:EquipmentType
    A category of equipment.
  gist:GeneralMediaType
    The real-world media type for content.
  gist:MediaType
    A digitized type that computer applications can recognize.
  gist:Medium
    A physical material on which a work can be rendered, represented, or implemented.
  gist:PhysicalActionType
    A category indicating the type of an action based on its effect in the physical world.
  gist:PhysicalAddressType
    A category indicating local customary characterizations of physical addresses.
  gist:ProductCategory
    Any of many ways of categorizing products.
  gist:Tag
    A term in a folksonomy used to categorize things. Tags can be made up on the fly by users.
gist:Commitment [defined]
  A promise made by a single party to one or more parties to do or not do something or act in a particular way.
gist:Component
  Something that, while having an independent existence, is inherently part of or designed to be part of a larger entity, such as a system or network.
  gist:NetworkNode
    A node in a network.
gist:Composite
  Something which is made up of various parts or elements that are independently identifiable.
  gist:Collection
    A grouping of things.
    gist:UnitGroup
      A collection of units of measure that can all be used to measure the same aspects.
gist:ContemporaryEvent [defined]
  An event that has started but has not yet ended.
gist:Content
  Information available in some medium.
  gist:Address
    A reference to a place (real or virtual) that can be located by some routing algorithm and where messages or things can be sent or received.
    gist:ElectronicAddress
      An address referring to a locatable virtual place that does not physically exist but is made by software or electronics to appear to do so.
    gist:PhysicalAddress [defined]
      An address that refers to a locatable place within the physical universe.
  gist:ContentExpression
    Intellectual property reduced to text, audio, etc.  If it contains text (written or spoken), it will be expressed in a language.
gist:ContingentEvent [defined]
  An event with a probability of happening in the future, and usually dependent upon some other event or condition.
gist:ContingentObligation [defined]
  An obligation that is not yet firm. There is some contingent event whose occurrence will cause the obligation to become firm.
gist:Contract [defined]
  An agreement which can be enforced by law.
gist:ControlledVocabulary [defined]
  A collection of terms approved and managed by some organization or person.
gist:CountryGeoRegion [defined]
  A geographic region governed by exactly one country government.
gist:CountryGovernment [defined]
  A government organization which asserts both sovereignty (i.e., it is not governed by some other government organization) and governance over an entit...
gist:Equipment [defined]
  Human-made, tangible property other than land or buildings used to perform a task or activity.
gist:Event
  Something that occurs over a period of time, often characterized as an activity being carried out by some person, organization, or software applicatio...
  gist:Determination
    An event whose purpose is to establish a specific result, value, or outcome, usually by research, measuring, evaluating, or calculating.
  gist:Transaction
    An exchange or transfer of goods, services, or funds.
gist:FormattedContent [defined]
  Content which is in a particular format.
gist:GeoLocation
  A physical location, with the earth as a frame of reference.
  gist:GeoPoint [defined]
    An individual point on or above the Earth's surface, identified by latitude, longitude and altitude. Altitude is the distance measured from sea level....
gist:GeoRegion
  A bounded region (or set of regions) on the surface of the Earth.
gist:GeoRoute [defined]
  An ordered set of geographic points that defines a path from a starting point to an ending point.
gist:GeoVolume [defined]
  A three-dimensional space on or near the surface of the Earth, such as an oil reservoir, the body of a lake, or an airspace.
gist:GovernedGeoRegion [defined]
  A geographic region governed by at least one government organization.
gist:HistoricalEvent [defined]
  An event which occurred in time, with an actual end earlier than the present moment.
gist:ID [defined]
  Content that is used to uniquely identify something or someone.
gist:IntellectualProperty
  An intangible work, invention, or concept, independent of its being expressed in text, audio, video, image, or live performance. IP can also be tacit ...
  gist:KnowledgeConcept
    An abstract concept that arises from the distillation of experience. It is similar to a category but, rather than being a simple tag, it has rich stru...
gist:Intention
  A goal, desire, or aspiration.
  gist:Function
    The activity that a human-made item is intended to perform.
  gist:Requirement
    The obligation of a person or organization to behave in a certain way.
  gist:Specification
    One or more characteristics that specify what it means to be a particular type of thing, such as a material, product, service or event. A specificatio...
    gist:CatalogItem
      A description of a product or service to be delivered, given in a sufficient level of detail that a receiver could determine whether delivery constitu...
    gist:ContractTerm
      A specification of some aspect of a contract.
    gist:EventSpecification
      A characterization of an event that might happen.
gist:IntergovernmentalOrganization [defined]
  An organization whose members are government organizations. This can comprise regional, municipal, state/province, or national level entities.
gist:Language
  A recognized, organized set of symbols and grammar.
gist:LivingThing [defined]
  Something that is currently, or at some point in time was, alive.
gist:Magnitude [defined]
  The amount of a measurable characteristic (aspect).
  gist:ReferenceValue
    A magnitude that was neither measured nor estimated but set by fiat.
gist:Message [defined]
  A specific instance of content sent from a sender to at least one other recipient.
gist:Network [defined]
  A composite consisting of nodes connected by links.
gist:NetworkLink [defined]
  An abstract representation of the connection between two or more nodes in a network.
gist:Offer [defined]
  A contingent commitment to buy, sell, swap or provide one or more described or identified goods or services in exchange for another (or others).
gist:OrderedCollection [defined]
  A collection whose members are ordered in some way.
gist:OrderedMember [defined]
  A member of an ordered collection serving as a proxy for a real world item, which can appear in different orders in different collections. The ordered...
gist:Organization
  A structured entity formed to achieve specific goals, typically involving members with defined roles.
  gist:GovernmentOrganization
    An independent organization exercising political and/or regulatory authority over a political unit, people, geographical region, etc., as well as perf...
gist:Permission [defined]
  A description of things one is permitted to do.
gist:Person [defined]
  A human being who was or is alive.
gist:PhysicalEvent [defined]
  An event that can be said to have occurred at some place in space.
gist:PhysicalIdentifiableItem
  A discrete physical object which, if subdivided, will result in parts that are distinguishable in nature from the whole and in general also from the o...
  gist:Landmark
    Something permanently attached to the Earth.
    gist:Building
      A relatively permanent man-made structure situated on a plot of land, having a roof and walls, commonly used for dwelling, entertaining, or working.
gist:PhysicalSubstance
  An undifferentiated amount of physical material which, when subdivided, results in each part being indistinguishable in nature from the whole and from...
gist:ProductSpecification [defined]
  Offering something which could be physically warehoused or digitally stored.
gist:Project [defined]
  A task, usually of longer duration, made up of other tasks.
gist:RenderedContent [defined]
  Content which has been physically expressed.
gist:Restriction [defined]
  A description of things one is prevented from doing.
gist:ScheduledEvent [defined]
  An event with a planned start datetime.
gist:ScheduledTask [defined]
  A task with a planned start datetime.
gist:SchemaMetaData
  Superclass for all types of metadata.
gist:ServiceSpecification [defined]
  A description of something that can be done for a person or organization (which produces some form of an act).
gist:SubCountryGovernment [defined]
  The government of a governed geographic region other than a country which is under the direct or indirect control of a country government.
gist:System [defined]
  A composite with component parts that contribute to the goal of the system.
gist:Task [defined]
  An activity or piece of work that is either proposed, planned, scheduled, underway, or completed.
gist:TaskTemplate [defined]
  An outline of a task of a particular type, which is the basis for executing such tasks.
gist:Template
  Something used to make objects in its own image.
gist:TemporalRelation
  A relationship existing for a period of time.
gist:Text [defined]
  Content expressed as words and numbers.
gist:TimeInterval
  A span of time with a known start time, end time, and duration. As long as two of the three are known, the third can be inferred.
gist:UnitOfMeasure
  A standard amount used to measure or specify things.

---

## Object Properties

These connect instances to other instances.

gist:allows
  Relates a permission to a particular activity or type of activity it allows.
gist:comesFromPlace
  Relates something to its place of origin.
gist:conformsTo
  The subject is consistent with or satisfies the requirements, rules, or expectations established by the object.
gist:contributesTo
  Relates a part of a system to the system whose goals or function it contributes to.
gist:goesToPlace
  Relates something to its destination place.
gist:hasAccuracy
  Relates a magnitude to another magnitude that describes its accuracy.
  [Range: gist:Magnitude]
gist:hasAddend
  Relates an aspect to another aspect that is an additive component of it.
gist:hasAddress
  Relates something to its physical or electronic address.
  [Range: gist:Address]
gist:hasAspect
  Relates a magnitude to its aspect (measurable characteristic).
  [Range: gist:Aspect]
gist:hasBiologicalParent
  Relates a living thing to its biological parent.
  [Domain: gist:LivingThing; Range: gist:LivingThing]
gist:hasBroader
  Relates a thing to another thing with a broader meaning.
  gist:hasDirectBroader
    Relates a thing to another thing with a broader meaning, when there is no intermediate between them.
  gist:hasUniqueBroader
    Relates a thing to a unique other thing with a broader meaning.
gist:hasDivisor
  Relates a unit of measure to another unit of measure that is a divisor, or relates an aspect to another aspect that is a...
gist:hasGoal
  Relates something to the end towards which it directs effort.
gist:hasIncumbent
  Relates a position to the thing or person that currently holds that position.
gist:hasMagnitude
  Relates a thing to a magnitude.
  [Range: gist:Magnitude]
gist:hasMultiplier
  Relates a unit of measure to another unit of measure that is a factor, or relates an aspect to another aspect that is a ...
gist:hasNavigationalParent
  Relates a child category to a parent category in an informal (e.g., faceted) hierarchy.
  gist:hasUniqueNavigationalParent
    Relates a subject category to a unique parent category in an informal (e.g., faceted) hierarchy.
gist:hasParticipant
  Relates something (e.g. an agreement) to things that play a role, or take part or are otherwise involved in some way.
  gist:comesFromAgent
    Relates something to the originating agent.
  gist:goesToAgent
    Relates something to the agent that receives it.
  gist:hasGiver
    Relates something to the participant that provides it.
  gist:hasParty
    Relates an event, agreement, or obligation to a participating person or organization.
  gist:hasRecipient
    Relates something to the participant that receives or is intended to receive it.
gist:hasPhysicalLocation
  Relates something to its physical location.
  [Range: gist:GeoLocation]
gist:hasSubtrahend
  Relates an aspect to another aspect that is a subtracted component of it.
gist:hasUnitGroup
  Relates an aspect to a unit group. The aspect can be measured using any of the members of the unit group.
  [Domain: gist:Aspect; Range: gist:UnitGroup]
gist:hasUnitOfMeasure
  Relates a magnitude to its unit of measure.
  [Domain: gist:Magnitude; Range: gist:UnitOfMeasure]
gist:isAbout
  Subject matter of a document.
  [Domain: gist:Content]
gist:isAffectedBy
  Relates an affected thing to the source of the effect.
gist:isAllocatedBy
  Relates something to whomever or whatever assigns or distributes it.
gist:isAssignmentOf
  Relates an assignment to the resource it assigns.
gist:isAssignmentTo
  Relates something (typically an assignment) to the thing the resource is assigned to, such as a project, position, organ...
gist:isBasedOn
  The object is a foundation for, a starting point for, gave rise to, or justifies the subject.
gist:isCategorizedBy
  Relates something to a taxonomy term or other less formally defined classification.
gist:isConnectedTo
  A non-owning, non-causal, non-subordinate (i.e., peer-to-peer) relationship.
gist:isExpressedIn
  Relates something to the language it is expressed in.
gist:isGeoContainedIn
  Relates one geographic location to another that contains it.
  [Domain: gist:GeoLocation; Range: gist:GeoLocation]
gist:isGovernedBy
  Relates an entity to another entity that controls, directs, determines or has a guiding influence or authority over it.
gist:isIdentifiedBy
  Relates something to a content object that uniquely identifies it.
  [Range: gist:ID]
gist:isMadeUpOf
  Relates something to a substance that it is made up of.
  [Range: gist:PhysicalSubstance]
gist:isMemberOf
  Relates a member individual to the thing, such as a collection or organization, that it is a member of.
  gist:isFirstMemberOf
    Relates the first member of an ordered collection to the collection.
    [Domain: gist:OrderedMember; Range: gist:OrderedCollection]
gist:isPartOf
  The relationship between a part and a whole where the part has independent existence.
  gist:isDirectPartOf
    The relationship between a part and a whole where the part has independent existence and there are no other parts in bet...
gist:isProducedBy
  Relates something to the thing that created, composed, or brought it into existence.
gist:isRecognizedBy
  Relates something to a party that formally acknowledges its existence, validity, or legality.
gist:isRenderedOn
  Relates content to the media on which it is rendered.
gist:isTriggeredBy
  Relates a contingency, such as an event or obligation, to the event that gives rise to it.
gist:isUnderJurisdictionOf
  Relates a law, contract, etc., to the system of law or government which has the power, right, or authority to interpret ...
gist:links
  Relates a network link to a network node that it connects to another node. Used when the connection is undirected or the...
  gist:linksFrom
    Relates a network link to its origin network node. Unlike the superproperty, this represents a directed connection.
  gist:linksTo
    Relates a network link to its destination network node. Unlike the superproperty, this represents a directed connection.
gist:occursIn
  Relates something, such as an event, to the geographic location where it did, does, or will happen.
gist:offersToProvide
  Relates an offer to the thing being made available for exchange.
gist:offersToReceive
  Relates an offer to the thing expected in return for the offered item.
gist:owns
  Relates a party to something that it possesses and controls.
gist:precedes
  A generic ordering relation indicating that the subject comes before the object.
  gist:precedesDirectly
    A generic ordering relation indicating that the subject comes immediately before the object.
gist:prevents
  Relates an intention to behavior that it prohibits.
  [Domain: gist:Intention; Range: gist:Behavior]
gist:providesOrderFor
  Links a member of an ordered collection to the real-world item it represents in that collection.
  [Domain: gist:OrderedMember]
gist:refersTo
  Relates something to another resource that it points to, indicates, or references.
gist:requires
  The subject needs the object or makes it necessary, mandatory, or compulsory.

---

## Datatype Properties

These connect instances to literal values (strings, numbers, dates).

gist:atDateTime
  The date and time at which something did or will occur, with variants for precision, start and end, and actual vs. plann...
  [Range: xsd:dateTime]
  gist:endDateTime
    The date and time that something ends.
    [Range: xsd:dateTime]
    gist:actualEndDateTime
      The actual date and time that something ended, with no implied precision.
      [Range: xsd:dateTime]
      gist:actualEndDate
        The actual date that something ended, with precision of one day.
        [Range: xsd:dateTime]
        gist:deathDate
          The date some living thing died.
          [Range: xsd:dateTime]
      gist:actualEndMicrosecond
        The actual time that something ended, expressed as a system time used for timestamps.
        [Range: xsd:dateTime]
      gist:actualEndMinute
        The actual date and time that something ended, with precision of one minute.
        [Range: xsd:dateTime]
      gist:actualEndYear
        The actual date that something ended, with precision of one year.
        [Range: xsd:dateTime]
    gist:plannedEndDateTime
      The date that something is or was planned to end, with no implied precision.
      [Range: xsd:dateTime]
      gist:plannedEndDate
        The date that something is or was planned to end, with precision of one day.
        [Range: xsd:dateTime]
      gist:plannedEndMinute
        The date and time that something is or was planned to end, with precision of one minute.
        [Range: xsd:dateTime]
      gist:plannedEndYear
        The date that something is or was planned to end, with precision of one year.
        [Range: xsd:dateTime]
  gist:isRecordedAt
    The date that something was posted (which is not necessarily the date it occurred). It must be after the date of occurre...
  gist:startDateTime
    The date and time that something starts.
    [Range: xsd:dateTime]
    gist:actualStartDateTime
      The actual date and time that something started, with no implied precision.
      [Range: xsd:dateTime]
      gist:actualStartDate
        The actual date that something started, with precision of one day.
        [Range: xsd:dateTime]
      gist:actualStartMicrosecond
        The actual time that something started, expressed as a system time used for timestamps.
        [Range: xsd:dateTime]
      gist:actualStartMinute
        The actual date and time that something started, with precision of one minute.
        [Range: xsd:dateTime]
      gist:actualStartYear
        The actual date that something started, with precision of one year.
        [Range: xsd:dateTime]
    gist:birthDate
      The date some living thing was or will be born, with precision of one day.
      [Range: xsd:dateTime]
    gist:plannedStartDateTime
      The date and time that something is or was planned to start, with no implied precision.
      [Range: xsd:dateTime]
      gist:plannedStartDate
        The date that something is or was planned to start, with precision of one day.
        [Range: xsd:dateTime]
      gist:plannedStartMinute
        The date and time that something is or was planned to start, with precision of one minute.
        [Range: xsd:dateTime]
      gist:plannedStartYear
        The date that something is or was planned to start, with precision of one year.
        [Range: xsd:dateTime]
gist:containedText
  A string that is closely associated with an individual.
  gist:encryptedText
    Encoded text produced from readable data by an algorithm so that it can only be understood or restored with a decryption...
    [Range: xsd:string]
  gist:uniqueText
    The unique string value of some content object, to be used when there is no possibility of having more than one value.
gist:conversionFactor
  A value that relates a unit of measure to units of the International System of Units.
  [Domain: gist:UnitOfMeasure]
gist:conversionOffset
  A value used along with a conversion factor to relate a unit to its corresponding unit in the International System of Un...
  [Domain: gist:UnitOfMeasure; Range: xsd:decimal]
gist:description
  A statement about someone or something's attributes or characteristics.
gist:exponentOfAmpere
  The exponent of ampere in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfBit
  The exponent of bit in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfCandela
  The exponent of candela in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfKelvin
  The exponent of Kelvin in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfKilogram
  The exponent of kilogram in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfMeter
  The exponent of meter in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfMole
  The exponent of mole in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfNumber
  The exponent of number in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfOther
  Indicates whether a unit of measure can be expressed in terms of the standard exponents (as shown in the examples).
  [Range: xsd:decimal]
gist:exponentOfRadian
  The exponent of radian in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfSecond
  The exponent of second in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfSteradian
  The exponent of steradian in a product of powers of base units.
  [Range: xsd:decimal]
gist:exponentOfUSDollar
  The exponent of US Dollar in a product of powers of base units.
  [Range: xsd:decimal]
gist:idText
  A text string that identifies an individual.
  [Range: xsd:string]
gist:latitude
  Degrees above or below the equator.
  [Domain: gist:GeoPoint; Range: xsd:double]
gist:longitude
  Degrees from the prime meridian.
  [Domain: gist:GeoPoint; Range: xsd:double]
gist:name
  Relates an individual to (one of) its name(s).
gist:numericValue
  The actual value of a magnitude.
gist:sequence
  For ordering ordered lists.
  [Range: xsd:integer]
gist:symbol
  A symbol for something using only ASCII characters.

---

## Statistics
- Classes: 96 (45 defined, 51 primitive)
- Object Properties: 65
- Datatype Properties: 50
