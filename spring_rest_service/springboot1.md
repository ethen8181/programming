

The RESTFUL Service we would create in this course:

Social Media Application

- Retrieve all user : GET /users
- Create a user : POST /users
- Retrieve one user : GET /users/{id}
- Delete a user : DELETE /users/{id}

A user can create many posts. So post has a many to one relationship with user.

- Retrieve all posts for a user : GET /users/{id}/posts
- Create a posts for a user - POST /users/{id}/posts
- Retrieve details of a post - GET /users/{id}/posts/{post_id}
