class CommentModel:
    def __init__(self, id, created_at, post_id, user_id, description):
        self.id = id
        self.created_at = created_at
        self.post_id = post_id
        self.user_id = user_id
        self.description = description