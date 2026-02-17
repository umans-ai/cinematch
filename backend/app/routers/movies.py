from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Movie, Room, Participant, Vote
from ..schemas import MovieResponse

router = APIRouter()

# Static movie list for MVP
STATIC_MOVIES = [
    {"title": "The Shawshank Redemption", "year": 1994, "genre": "Drama", "description": "Two imprisoned men bond over a number of years..."},
    {"title": "The Godfather", "year": 1972, "genre": "Crime, Drama", "description": "The aging patriarch of an organized crime dynasty..."},
    {"title": "The Dark Knight", "year": 2008, "genre": "Action, Crime, Drama", "description": "When the menace known as the Joker wreaks havoc..."},
    {"title": "Pulp Fiction", "year": 1994, "genre": "Crime, Drama", "description": "The lives of two mob hitmen, a boxer..."},
    {"title": "Inception", "year": 2010, "genre": "Action, Sci-Fi", "description": "A thief who steals corporate secrets through dream-sharing technology..."},
    {"title": "Fight Club", "year": 1999, "genre": "Drama", "description": "An insomniac office worker and a devil-may-care soapmaker..."},
    {"title": "Forrest Gump", "year": 1994, "genre": "Drama, Romance", "description": "The presidencies of Kennedy and Johnson, the Vietnam War..."},
    {"title": "The Matrix", "year": 1999, "genre": "Action, Sci-Fi", "description": "A computer hacker learns about the true nature of his reality..."},
    {"title": "Goodfellas", "year": 1990, "genre": "Biography, Crime, Drama", "description": "The story of Henry Hill and his life in the mob..."},
    {"title": "The Silence of the Lambs", "year": 1991, "genre": "Crime, Drama, Thriller", "description": "A young FBI cadet must receive the help of an incarcerated..."},
    {"title": "Interstellar", "year": 2014, "genre": "Adventure, Drama, Sci-Fi", "description": "A team of explorers travel through a wormhole in space..."},
    {"title": "Parasite", "year": 2019, "genre": "Comedy, Drama, Thriller", "description": "Greed and class discrimination threaten the newly formed symbiotic relationship..."},
    {"title": "The Green Mile", "year": 1999, "genre": "Crime, Drama, Fantasy", "description": "The lives of guards on Death Row are affected by one of their charges..."},
    {"title": "Gladiator", "year": 2000, "genre": "Action, Adventure, Drama", "description": "A former Roman General sets out to exact vengeance against the corrupt emperor..."},
    {"title": "The Lion King", "year": 1994, "genre": "Animation, Adventure, Drama", "description": "Lion prince Simba and his father are targeted by his bitter uncle..."},
    {"title": "Back to the Future", "year": 1985, "genre": "Adventure, Comedy, Sci-Fi", "description": "Marty McFly, a 17-year-old high school student, is accidentally sent..."},
    {"title": "The Avengers", "year": 2012, "genre": "Action, Adventure, Sci-Fi", "description": "Earth's mightiest heroes must come together and learn to fight as a team..."},
    {"title": "Jurassic Park", "year": 1993, "genre": "Action, Adventure, Sci-Fi", "description": "A pragmatic paleontologist touring an almost complete theme park..."},
    {"title": "Titanic", "year": 1997, "genre": "Drama, Romance", "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist..."},
    {"title": "The Departed", "year": 2006, "genre": "Crime, Drama, Thriller", "description": "An undercover cop and a mole in the police attempt to identify each other..."},
    {"title": "Whiplash", "year": 2014, "genre": "Drama, Music", "description": "A promising young drummer enrolls at a cut-throat music conservatory..."},
    {"title": "La La Land", "year": 2016, "genre": "Comedy, Drama, Music", "description": "While navigating their careers in Los Angeles, a pianist and an actress..."},
    {"title": "The Social Network", "year": 2010, "genre": "Biography, Drama", "description": "As Harvard student Mark Zuckerberg creates the social networking site..."},
    {"title": "Mad Max: Fury Road", "year": 2015, "genre": "Action, Adventure, Sci-Fi", "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler..."},
    {"title": "Get Out", "year": 2017, "genre": "Horror, Mystery, Thriller", "description": "A young African-American visits his white girlfriend's parents for the weekend..."},
    {"title": "Spider-Man: Into the Spider-Verse", "year": 2018, "genre": "Animation, Action, Adventure", "description": "Teen Miles Morales becomes the Spider-Man of his universe..."},
    {"title": "Coco", "year": 2017, "genre": "Animation, Adventure, Family", "description": "Aspiring musician Miguel, confronted with his family's ancestral ban on music..."},
    {"title": "Up", "year": 2009, "genre": "Animation, Adventure, Comedy", "description": "78-year-old Carl Fredricksen travels to Paradise Falls in his house..."},
    {"title": "WALL·E", "year": 2008, "genre": "Animation, Adventure, Family", "description": "In a distant, but not so unrealistic, future where mankind has abandoned earth..."},
    {"title": "Inside Out", "year": 2015, "genre": "Animation, Adventure, Comedy", "description": "After young Riley is uprooted from her Midwest life and moved to San Francisco..."},
    {"title": "Finding Nemo", "year": 2003, "genre": "Animation, Adventure, Comedy", "description": "After his son is captured in the Great Barrier Reef and taken to Sydney..."},
    {"title": "Toy Story", "year": 1995, "genre": "Animation, Adventure, Comedy", "description": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure..."},
    {"title": "Monsters, Inc.", "year": 2001, "genre": "Animation, Adventure, Comedy", "description": "In order to power the city, monsters have to scare children so that they scream..."},
    {"title": "Ratatouille", "year": 2007, "genre": "Animation, Adventure, Comedy", "description": "A rat who can cook makes an unusual alliance with a young kitchen worker..."},
    {"title": "The Incredibles", "year": 2004, "genre": "Animation, Action, Adventure", "description": "A family of undercover superheroes, while trying to live the quiet suburban life..."},
    {"title": "Shrek", "year": 2001, "genre": "Animation, Adventure, Comedy", "description": "A mean lord exiles fairytale creatures to the swamp of a grumpy ogre..."},
    {"title": "Zootopia", "year": 2016, "genre": "Animation, Adventure, Comedy", "description": "In a city of anthropomorphic animals, a rookie bunny cop and a cynical con artist..."},
    {"title": "Moana", "year": 2016, "genre": "Animation, Adventure, Comedy", "description": "In Ancient Polynesia, when a terrible curse incurred by the Demigod Maui reaches..."},
    {"title": "Frozen", "year": 2013, "genre": "Animation, Adventure, Comedy", "description": "When the newly crowned Queen Elsa accidentally uses her power to turn things into ice..."},
    {"title": "Tangled", "year": 2010, "genre": "Animation, Adventure, Comedy", "description": "The magically long-haired Rapunzel has spent her entire life in a tower..."},
    {"title": "The Grand Budapest Hotel", "year": 2014, "genre": "Adventure, Comedy, Crime", "description": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years..."},
    {"title": "Moonlight", "year": 2016, "genre": "Drama", "description": "A young African-American man grapples with his identity and sexuality..."},
    {"title": "Spotlight", "year": 2015, "genre": "Biography, Crime, Drama", "description": "The true story of how the Boston Globe uncovered the massive scandal..."},
    {"title": "Birdman", "year": 2014, "genre": "Comedy, Drama", "description": "A washed-up superhero actor attempts to revive his fading career by writing..."},
    {"title": "12 Years a Slave", "year": 2013, "genre": "Biography, Drama, History", "description": "In the antebellum United States, Solomon Northup, a free black man from upstate New York..."},
    {"title": "Django Unchained", "year": 2012, "genre": "Drama, Western", "description": "With the help of a German bounty hunter, a freed slave sets out to rescue his wife..."},
    {"title": "Inglourious Basterds", "year": 2009, "genre": "Adventure, Drama, War", "description": "In Nazi-occupied France during World War II, a plan to assassinate Nazi leaders..."},
    {"title": "The Prestige", "year": 2006, "genre": "Drama, Mystery, Sci-Fi", "description": "After a tragic accident, two stage magicians engage in a battle to create..."},
    {"title": "Memento", "year": 2000, "genre": "Mystery, Thriller", "description": "A man with short-term memory loss attempts to track down his wife's murderer..."},
    {"title": "Eternal Sunshine of the Spotless Mind", "year": 2004, "genre": "Drama, Romance, Sci-Fi", "description": "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories..."},
]


def seed_movies(db: Session):
    """Seed the database with static movies if empty."""
    if db.query(Movie).count() == 0:
        for movie_data in STATIC_MOVIES:
            movie = Movie(**movie_data)
            db.add(movie)
        db.commit()


@router.get("", response_model=List[MovieResponse])
def get_movies(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Seed movies if needed
    seed_movies(db)

    movies = db.query(Movie).all()
    return movies


@router.get("/unvoted", response_model=List[MovieResponse])
def get_unvoted_movies(code: str, participant_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    seed_movies(db)

    # Get movies this participant hasn't voted on yet
    voted_movie_ids = [
        vote.movie_id for vote in db.query(Vote).filter(
            Vote.participant_id == participant_id
        ).all()
    ]

    movies = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all()
    return movies
