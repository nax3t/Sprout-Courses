# Sproute Courses - Spike 1
### User stories:

#### A user should be able to upload a video file to cloudinary

- what's needed? a page with a form that accepts video files
    - requires a url, a view, and template
        - url - done
        - view
            - logic for GET and POST requests
                - GET - done
                - POST - done        
        - template - done
    - logic will be moved into a background job so as not to block http layer
