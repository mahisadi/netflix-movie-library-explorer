Lets start with data layer first .. data model design is the foundation of the apps.

Files are in the google drive. lets consider this as source. i.e. source=google_drive. Requirement is to fetch movie files. In future it could be other type of files. Lets consider this as contentType. i.e contentType=movies

Now, folders structure is zig zag with {genre}/{subgenre}/{year} of release. Lets define schema for one record and put it in the drive with happy path. the record may not contain, genre or subgenre or year information. We may need to get this from folder path.

sample json file.

{

  "title": "The Social Network”,
  "imdb_rating": 7.8,
  "language": "English",
  "country": "United States",
  "stars": [
    "Jesse Eisenberg",
    "Andrew Garfield",
    "Justin Timberlake",
    "Armie Hammer"
  ],
  "director": "David Fincher",
  "writer": "Aaron Sorkin",
  "popu": 88,
  "production_house": "Sony Pictures",
  "movie_plot": "As Harvard student Mark Zuckerberg creates the social networking site that would become known as Facebook, he is sued by the twins who claimed he stole their idea.",
  "awards": [
    "Academy Award for Best Adapted Screenplay",
    "Golden Globe for Best Motion Picture - Drama"
  ]
}

Drop it in google drive .. follow shared steps and access the file programatically.




# For the Connectors

# Data Strategy

Once the connector run keep the strctured data into s3 folders named after source and content type. Its best practice to main source of truth for the processed data.
This is crucial and avoids DRY principle to process the data. In future, if we move away from one cloud platform to another, we don't need to lots of effort.


