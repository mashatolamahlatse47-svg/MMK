from flask import Flask

from database import init_database

app = Flask(__name__)

init_database()


@app.route("/")
def home():
    return """
    <!doctype html>
    <html>
    <head>
        <title>MMK Digital Factory</title>
    </head>
    <body>
        <h1>MMK DIGITAL FACTORY</h1>
        <p>Internal Factory Dashboard</p>
        <p>Engine status: ONLINE</p>
    </body>
    </html>
    """


from templates_dashboard import dashboard
from opportunities import opportunity_page
from opportunity_list import opportunity_list, transition_opportunity_route
from products import product_page
from services import service_page
from members import member_page
from manufacturing import manufacturing_page
from projects import project_page

app.add_url_rule("/dashboard", "dashboard", dashboard)
app.add_url_rule("/opportunities", "opportunities", opportunity_list)
app.add_url_rule(
    "/opportunities/<opportunity_id>/transition",
    "transition_opportunity_route",
    transition_opportunity_route,
    methods=["POST"],
)
app.add_url_rule(
    "/products/new",
    "new_product",
    product_page,
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/services/new",
    "new_service",
    service_page,
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/opportunities/new",
    "new_opportunity",
    opportunity_page,
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/projects/new",
    "new_project",
    project_page,
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/manufacturing/new",
    "new_manufacturing",
    manufacturing_page,
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/members/new",
    "new_member",
    member_page,
    methods=["GET", "POST"],
)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=False)
