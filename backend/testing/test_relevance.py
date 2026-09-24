from ..src.relevance import compute_relevance

# Testing relevant query with boston housing
def test_relevant_boston():
    boston_score = compute_relevance("suburb homes 1978", "Boston Housing", [
        "earth and nature",
        "education",
        "real estate",
        "social issues and advocacy"
    ], "housing")
    assert boston_score >= 0.4, "Relevant boston housing query failed"


# Testing irrelevant query with boston housing
def test_irrelevant_boston_relevance():
    iboston_score = compute_relevance("what's the weather like today", "California Housing Prices", [
        "earth and nature",
        "education",
        "real estate",
        "social issues and advocacy"
    ], "housing")
    assert iboston_score < 0.4, "Irrelevant boston housing query failed"

# Testing relevant query with facebook politics
def test_facebook_relevance():
    fb_score = compute_relevance("facebook fake news", "Fact-Checking Facebook Politics Pages", [
        "politics",
        "internet",
        "social networks"
    ], "politics")
    assert fb_score >= 0.4, "Relevant facebook politics query failed"
# Testing irrelevant query with facebook politics
def test_irrelevant_facebook_relevance():
    ifb_score = compute_relevance("what's the weather like today","Fact-Checking Facebook Politics Pages", [
        "politics",
        "internet",
        "social networks"
    ], "politics")
    assert ifb_score < 0.4, "Irrelevant facebook politics query failed"

def test_relevant_sports_car():
    sc_score = compute_relevance("What is the most expensive car?", "Sports Car Prices dataset", [
        "beginner",
        "intermediate",
        "tabular",
        "regression",
        "retail and shopping"
    ], "sports")
    assert sc_score >= 0.4, "Relevant sports car dataset failed"

def test_irrelevant_sports_car():
    isc_score = compute_relevance("What is the best color for collared shirts?", "Sports Car Prices dataset", [
        "beginner",
        "intermediate",
        "tabular",
        "regression",
        "retail and shopping"
    ], "sports")
    assert isc_score < 0.4, "Irelevant sports car dataset failed"

if __name__ == "__main__":
    test_relevant_boston()
    test_irrelevant_boston_relevance()
    test_facebook_relevance()
    test_irrelevant_facebook_relevance()
    test_relevant_sports_car()
    test_irrelevant_sports_car()