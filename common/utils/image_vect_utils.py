import weaviate
import numpy as np

client = weaviate.Client(
  'http://0.0.0.0:4001',
  timeout_config=(100, 60)
)

def dist(id1, id2):
  def euclidean_distance(vec1, vec2):
    """Calculate the Euclidean distance between two vectors."""
    return np.linalg.norm(np.array(vec1) - np.array(vec2))
  
  # Fetch the vectors
  v1 = client.data_object.get_by_id(id1, ["imageVector"])
  v2 = client.data_object.get_by_id(id2, ["imageVector"])
  
  # Extract the vector data
  vec1 = v1["imageVector"]
  vec2 = v2["imageVector"]
  
  # Calculate and return the distance
  return euclidean_distance(vec1, vec2)

