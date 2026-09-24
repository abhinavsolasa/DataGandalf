from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def compute_relevance(input_query, title, tags, topic):
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    input_embedding = model.encode([input_query])
    title_embedding = model.encode([title])
    topic_embedding = model.encode([topic])

    

    similarity_scores_topic= cosine_similarity(input_embedding.reshape(1, -1), topic_embedding)[0][0]
    similarity_scores_title = cosine_similarity(input_embedding.reshape(1, -1), title_embedding)[0][0]
    tag_sum = 0

    l = len(tags)
    print(l, tags)
    if l == 0:
        tag_weight = 0
        tag_avg = 0
    elif l == 1:
        tag_embeddings = model.encode(tags)
        similarity_scores_tag = cosine_similarity(input_embedding.reshape(1, -1), tag_embeddings)[0]
        tag_weight = 0.111
        tag_avg = similarity_scores_tag[0]
    else:
        tag_embeddings = model.encode(tags)
        print(input_embedding, tag_embeddings)
        similarity_scores_tag = cosine_similarity(input_embedding.reshape(1, -1), tag_embeddings)[0]
        print(l, similarity_scores_tag)
        tag_weight = 0.111
        for i in range(len(tags)):
            tag_sum += similarity_scores_tag[i]
            tag_weight = (tag_weight - (tag_weight * (i + 1) * 0.0475))
            #print("current weight: ", tag_weight)
        
        tag_avg = tag_sum / len(tags)

    title_weight = 0.778
    topic_weight = 0.222
    #print("current weight: ", tag_weight)
    #print("Tag similarity avg: ", tag_avg)
    #print("Topic similarity: ", similarity_scores_topic)
    
    topic_weight = 0.222 - tag_weight

    relevance_score = (tag_weight * tag_avg) + (topic_weight * similarity_scores_topic) + (title_weight * similarity_scores_title)
    print(relevance_score)
    return relevance_score