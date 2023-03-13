import fire
import json
import requests

class CLI:
    def ai(self):
        from langchain.agents import load_tools
        from langchain.agents import initialize_agent
        from langchain.agents import Tool
        from langchain.llms import OpenAI

        # set OPENAI_API_KEY in your environment
        llm = OpenAI(temperature=0)

        def submit_feedback(feedback):
            # TODO: send feedback to a database
            return "Thanks for the feedback!"

        def api_request(path):
            url = f"https://deckofcardsapi.com/api{path}"
            response = requests.get(url)
            return json.loads(response.text)

        def shuffle(*args, **kwargs):
            deck_id = api_request("/deck/new/shuffle/?deck_count=1")["deck_id"]
            return json.dumps({"deck_id": deck_id})

        def draw(deck_id):
            card = api_request(f"/deck/{deck_id}/draw/?count=1")["cards"][0]["code"]
            return json.dumps({"card": card})

        hands = {
            "player": [],
            "opponent": [],
            "board": []
        }

        def add_to_player_hand(card):
            hands["player"].append(card)
            return json.dumps({"card":card})

        def add_to_opponent_hand(card):
            hands["opponent"].append(card)
            return json.dumps({"card":card})

        def get_player_hand(*args):
            return json.dumps({"cards":hands["player"]})

        def get_opponent_hand(*args):
            return json.dumps({"cards":hands["opponent"]})

        def add_to_board(card):
            hands["board"].append(card)
            return json.dumps({"card":card})

        ranks = {
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14
        }

        def highcard_get_winner(*args):
            p = hands["player"][0]
            o = hands["opponent"][0]

            rp = p[0]
            ro = o[0]

            nrp = ranks.get(rp)
            if nrp is None:
                nrp = int(rp)

            nro = ranks.get(ro)
            if nro is None:
                nro = int(ro)

            if nrp == 0:
                nrp = 10
            if nro == 0:
                nro = 10

            if nrp > nro:
                return json.dumps({"winner": "player"})
            elif nro > nrp:
                return json.dumps({"winner": "opponent"})
            else:
                return json.dumps({"winner": "tie"})

        tools = [#Tool(name="submit_feedback",
                 #     description="If you have suggestions for improvements to the tools, please submit them here.",
                 #     func=submit_feedback),
                 Tool(name="shuffle",
                      description="Get the deck_id of a freshly shuffled deck of cards.",
                      func=shuffle),
                 Tool(name="draw",
                      description="Draw the card on top of the deck with the given deck_id.",
                      func=draw),
                 Tool(name="add_to_player_hand",
                      description="Add a card to the player's hand.",
                      func=add_to_player_hand),
                 Tool(name="add_to_opponent_hand",
                      description="Add a card to the opponent's hand.",
                      func=add_to_opponent_hand),
                 Tool(name="add_to_board",
                      description="Add a card to the board.",
                      func=add_to_board),
                 Tool(name="get_player_hand",
                      description="Get the player's hand.",
                      func=get_player_hand),
                 Tool(name="get_opponent_hand",
                      description="Get the opponent's hand.",
                      func=get_opponent_hand),
                 Tool(name="highcard_get_winner",
                      description="Get the winner of the high card game.",
                      func=highcard_get_winner)
                 ]
        agent = initialize_agent(tools,
                                 llm,
                                 agent="zero-shot-react-description",
                                 verbose=True)
#        agent.run("Deal a hand of Texas Holdem between a player and an opponent.  No betting, but after dealing the player's hands, run out the flop, turn and river and announce the winning hand.")
        prompt = "Deal a hand of high card between a player and an opponent and announce both cards and the winner."
        print(f"Primary prompt: {prompt}")
        agent.run(prompt)


if __name__ == '__main__':
    fire.Fire(CLI)