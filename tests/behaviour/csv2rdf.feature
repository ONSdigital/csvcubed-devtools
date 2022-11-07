Feature: Test the csv2rdf step definitions

  Scenario: The csv2rdf step definition should successfully generate ttl
    Given the existing test-case file "csv2rdf/data.csv"
    And the existing test-case file "csv2rdf/data.csv-metadata.json"
    Then csv2rdf on "csv2rdf/data.csv-metadata.json" should succeed
    And the RDF should contain
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix skos: <http://www.w3.org/2004/02/skos/core#>.
      @prefix ui: <http://www.w3.org/ns/ui#>.

      <{{rdf_input_directory}}/data.csv#abba> a skos:Concept ;
          rdfs:label "ABBA" ;
          skos:inScheme <file:/tmp/data.csv#code-list> ;
          skos:notation "abba" ;
          ui:sortPriority 0 .
    """


    Scenario: The csv2rdf step definition on all CSV-Ws should successfully generate ttl
    Given the existing test-case file "csv2rdf/data.csv"
    And the existing test-case file "csv2rdf/data.csv-metadata.json"
    Then csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix skos: <http://www.w3.org/2004/02/skos/core#>.
      @prefix ui: <http://www.w3.org/ns/ui#>.

      <{{rdf_input_directory}}/data.csv#abba> a skos:Concept ;
          rdfs:label "ABBA" ;
          skos:inScheme <file:/tmp/data.csv#code-list> ;
          skos:notation "abba" ;
          ui:sortPriority 0 .
    """
