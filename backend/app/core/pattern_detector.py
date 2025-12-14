"""Pattern detection and document clustering."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models.database_models import Document, DocumentChunk
from app.core.vector_store import VectorStore
from app.utils.logger import logger


class PatternDetector:
    """Detect patterns and relationships between documents."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.similarity_threshold = 0.7
        self.min_cluster_size = 2
        self.max_clusters = 10

    def detect_similar_documents(
        self, document_id: int, db: Session, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to the given document.

        Args:
            document_id: The document to find similar documents for
            db: Database session
            top_k: Number of similar documents to return

        Returns:
            List of similar documents with similarity scores
        """
        # Get the document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return []

        # Get all chunks for this document
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .all()
        )

        if not chunks:
            logger.warning(f"No chunks found for document {document_id}")
            return []

        # Get embeddings for these chunks
        chunk_ids = [chunk.embedding_id for chunk in chunks if chunk.embedding_id]
        if not chunk_ids:
            logger.warning(f"No embeddings found for document {document_id}")
            return []

        try:
            # Get the first chunk's embedding as representative
            collection = self.vector_store.get_collection()
            query_embedding = collection.get(ids=[chunk_ids[0]], include=["embeddings"])

            if not query_embedding or not query_embedding["embeddings"]:
                return []

            # Search for similar chunks across all documents
            results = collection.query(
                query_embeddings=query_embedding["embeddings"],
                n_results=top_k * 5,  # Get more results to filter out same document
                include=["metadatas", "distances"],
            )

            # Group by document and calculate average similarity
            doc_similarities: Dict[int, List[float]] = {}
            doc_metadata: Dict[int, Dict[str, Any]] = {}

            for metadata, distance in zip(
                results["metadatas"][0], results["distances"][0]
            ):
                other_doc_id = metadata.get("document_id")
                if other_doc_id == document_id:  # Skip same document
                    continue

                similarity = 1 - distance  # Convert distance to similarity
                if similarity < self.similarity_threshold:
                    continue

                if other_doc_id not in doc_similarities:
                    doc_similarities[other_doc_id] = []
                    doc_metadata[other_doc_id] = metadata

                doc_similarities[other_doc_id].append(similarity)

            # Calculate average similarity per document
            similar_docs = []
            for doc_id, similarities in doc_similarities.items():
                avg_similarity = np.mean(similarities)
                similar_docs.append(
                    {
                        "document_id": doc_id,
                        "filename": doc_metadata[doc_id].get("filename", "Unknown"),
                        "similarity": float(avg_similarity),
                        "matching_chunks": len(similarities),
                    }
                )

            # Sort by similarity and return top_k
            similar_docs.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_docs[:top_k]

        except Exception as e:
            logger.error(f"Error detecting similar documents: {e}")
            return []

    def cluster_documents(
        self, db: Session, n_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cluster documents based on their embeddings.

        Args:
            db: Database session
            n_clusters: Number of clusters (auto-detected if None)

        Returns:
            Dictionary with cluster assignments and themes
        """
        try:
            # Get all documents with embeddings
            documents = (
                db.query(Document)
                .filter(Document.processing_status == "completed")
                .all()
            )

            if len(documents) < self.min_cluster_size:
                logger.warning(
                    f"Not enough documents to cluster (need at least {self.min_cluster_size})"
                )
                return {
                    "clusters": [],
                    "themes": [],
                    "total_documents": len(documents),
                    "n_clusters": 0,
                }

            # Collect document embeddings
            doc_embeddings = []
            doc_info = []

            collection = self.vector_store.get_collection()

            for doc in documents:
                # Get first chunk embedding as document representative
                chunks = (
                    db.query(DocumentChunk)
                    .filter(
                        DocumentChunk.document_id == doc.id,
                        DocumentChunk.embedding_id.isnot(None),
                    )
                    .limit(1)
                    .all()
                )

                if not chunks:
                    continue

                embedding_id = chunks[0].embedding_id
                result = collection.get(ids=[embedding_id], include=["embeddings"])

                if result and result["embeddings"]:
                    doc_embeddings.append(result["embeddings"][0])
                    doc_info.append(
                        {
                            "id": doc.id,
                            "filename": doc.filename,
                            "title": doc.title or doc.filename,
                        }
                    )

            if len(doc_embeddings) < self.min_cluster_size:
                logger.warning("Not enough document embeddings for clustering")
                return {
                    "clusters": [],
                    "themes": [],
                    "total_documents": len(doc_embeddings),
                    "n_clusters": 0,
                }

            # Determine optimal number of clusters
            if n_clusters is None:
                n_clusters = min(
                    self.max_clusters,
                    max(2, len(doc_embeddings) // 3),  # Roughly 3 docs per cluster
                )

            # Perform K-means clustering
            embeddings_array = np.array(doc_embeddings)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings_array)

            # Organize results by cluster
            clusters = []
            for cluster_id in range(n_clusters):
                cluster_doc_indices = np.where(cluster_labels == cluster_id)[0]
                cluster_docs = [doc_info[i] for i in cluster_doc_indices]

                if cluster_docs:
                    clusters.append(
                        {
                            "cluster_id": int(cluster_id),
                            "documents": cluster_docs,
                            "size": len(cluster_docs),
                            "centroid": kmeans.cluster_centers_[cluster_id].tolist(),
                        }
                    )

            # Generate theme names based on document titles
            themes = []
            for cluster in clusters:
                # Simple theme extraction: use most common words in titles
                titles = [doc["title"] for doc in cluster["documents"]]
                theme_name = f"Theme {cluster['cluster_id'] + 1}"

                # Try to extract common keywords
                words = []
                for title in titles:
                    words.extend(title.lower().split())

                if words:
                    # Get most common word (excluding common articles)
                    stop_words = {
                        "the",
                        "a",
                        "an",
                        "and",
                        "or",
                        "but",
                        "in",
                        "on",
                        "at",
                        "to",
                        "for",
                    }
                    filtered_words = [
                        w for w in words if w not in stop_words and len(w) > 3
                    ]
                    if filtered_words:
                        from collections import Counter

                        most_common = Counter(filtered_words).most_common(1)
                        if most_common:
                            theme_name = most_common[0][0].capitalize()

                themes.append(
                    {
                        "cluster_id": cluster["cluster_id"],
                        "theme_name": theme_name,
                        "document_count": cluster["size"],
                    }
                )

            return {
                "clusters": clusters,
                "themes": themes,
                "total_documents": len(doc_info),
                "n_clusters": n_clusters,
            }

        except Exception as e:
            logger.error(f"Error clustering documents: {e}")
            return {
                "clusters": [],
                "themes": [],
                "total_documents": 0,
                "n_clusters": 0,
                "error": str(e),
            }

    def suggest_connections(
        self, document_id: int, db: Session, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest potential connections between documents for the canvas.

        Args:
            document_id: The document to find connections for
            db: Database session
            threshold: Similarity threshold (uses default if None)

        Returns:
            List of suggested connections with confidence scores
        """
        if threshold is None:
            threshold = self.similarity_threshold

        similar_docs = self.detect_similar_documents(document_id, db, top_k=10)

        # Filter by threshold and format for canvas
        connections = []
        for doc in similar_docs:
            if doc["similarity"] >= threshold:
                connections.append(
                    {
                        "source_document_id": document_id,
                        "target_document_id": doc["document_id"],
                        "connection_type": "semantic_similarity",
                        "strength": doc["similarity"],
                        "confidence": "high" if doc["similarity"] > 0.85 else "medium",
                        "reason": f"Semantic similarity: {doc['similarity']:.2%}",
                        "matching_chunks": doc["matching_chunks"],
                    }
                )

        return connections

    def analyze_document_network(self, db: Session) -> Dict[str, Any]:
        """
        Analyze the overall document network structure.

        Args:
            db: Database session

        Returns:
            Network analysis with central documents, clusters, and metrics
        """
        try:
            documents = (
                db.query(Document)
                .filter(Document.processing_status == "completed")
                .all()
            )

            if len(documents) < 2:
                return {
                    "central_documents": [],
                    "isolated_documents": [],
                    "network_density": 0.0,
                    "total_connections": 0,
                    "total_documents": len(documents),
                }

            # Build similarity matrix
            doc_ids = [doc.id for doc in documents]
            n_docs = len(doc_ids)
            similarity_matrix = np.zeros((n_docs, n_docs))

            for i, doc_id in enumerate(doc_ids):
                similar = self.detect_similar_documents(doc_id, db, top_k=n_docs)
                for sim_doc in similar:
                    j = doc_ids.index(sim_doc["document_id"])
                    similarity_matrix[i, j] = sim_doc["similarity"]

            # Calculate centrality (sum of connections above threshold)
            centrality = np.sum(similarity_matrix > self.similarity_threshold, axis=1)

            # Find central documents (high connectivity)
            central_indices = np.argsort(centrality)[-5:][::-1]  # Top 5
            central_documents = []
            for idx in central_indices:
                if centrality[idx] > 0:
                    central_documents.append(
                        {
                            "document_id": doc_ids[idx],
                            "filename": documents[idx].filename,
                            "connections": int(centrality[idx]),
                            "centrality_score": float(centrality[idx] / n_docs),
                        }
                    )

            # Find isolated documents (no connections)
            isolated_indices = np.where(centrality == 0)[0]
            isolated_documents = [
                {"document_id": doc_ids[idx], "filename": documents[idx].filename}
                for idx in isolated_indices
            ]

            # Calculate network density
            total_possible_connections = n_docs * (n_docs - 1) / 2
            actual_connections = (
                np.sum(similarity_matrix > self.similarity_threshold) / 2
            )
            network_density = (
                actual_connections / total_possible_connections
                if total_possible_connections > 0
                else 0
            )

            return {
                "central_documents": central_documents,
                "isolated_documents": isolated_documents,
                "network_density": float(network_density),
                "total_connections": int(actual_connections),
                "total_documents": n_docs,
            }

        except Exception as e:
            logger.error(f"Error analyzing document network: {e}")
            return {
                "central_documents": [],
                "isolated_documents": [],
                "network_density": 0.0,
                "total_connections": 0,
                "total_documents": 0,
                "error": str(e),
            }
