# Project Context

Whitelabel project that can be replicated in a university library. The ideia is to have a chatbot where the students can use natural language to find books in its university library, returning best ranked alternatives with its basic informations and a map feature that we can have the specific location and way by the library's door. Since this is an MVP, we're showcasing a specific university called Anhembi Morumbi [website](https://landing.anhembi.br/?utm_source=google&utm_medium=cpc&utm_campaign=UAM_GRAD_TODOS_PERFORMANCE_GOOGLE_SEARCH_INSTITUCIONAL_262&utm_content=PURO_TODOS_UNIFICADA_V1_262&gclsrc=aw.ds&gad_source=1&gad_campaignid=21747620104&gbraid=0AAAAADruYn96mIzV7AHuC2swsL6CqmEQM&gclid=CjwKCAjwzLHPBhBTEiwABaLsSkRlCwHqddJ9YUz5ntcIn7aidWyuw6ZmRKGOXKgZq8ov0a1eFHtisRoCbqwQAvD_BwE)


We have two different personas: student and library admin.



## Student

Student persona has this basic UI with an input field, checkboxes to filter book type (HQs, books, journals,) and a send button. After sending the request, the page shows a loading then after having the return, it shows three best ranked books in a card format, each card has the book's title, author, year, and a button to see the map. Since we're building an MVP, the books will be mocked up. The UI must match what was configured in Admin profile, so it must have placeholders that are changed by those configurations.

## Admin

Admin persona has a dashboard to manage the books and the library's map. It also has the ability to change UI features like colors and the university logo (since our idea is to have multiple universities, but each one of them has a specific URL, foe example: ucla.our-library.com).


# Architecture

The chatbot will be built with AI Agents based on this project: [https://deepwiki.com/Karina-Lima/TransalteMyPrompt](https://deepwiki.com/Karina-Lima/TransalteMyPrompt). The main agents are:

1. Professor Agent: researches the topic by defining 4 essential subjects
2. Researcher Agent: based on the subjects, searches for books according to format types (comics) and selects 5 books
3. Educator Agent: creates a short "synopsis" for each book
4. Descriptive Agent: fetches metadata from the internet (Amazon)

Its frontend will be created in React. Our database now is the internet, so we'll use Google Books API.

The admin dashboard is essentially a CRUD application with a Flask backend and a React frontend.
It's also required an API to authenticate as student and also as an admin.


# Rules

All UI must be written in Brazilian Portuguese. With being said, the chatbot must follow colors and logos set up as configured in the admin dashboard.