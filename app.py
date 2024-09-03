from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load the model and tokenizer
model_name = "distilbert-base-uncased-finetuned-sst-2-english"  # You might want to fine-tune a model for better results
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create a text classification pipeline
nlp_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    tags = db.Column(db.String(200), nullable=False)

    def set_tags(self, tags):
        if isinstance(tags, list):
            self.tags = json.dumps(tags)
        else:
            self.tags = tags  # For backwards compatibility

    def get_tags(self):
        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            # For backwards compatibility
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date.strftime("%Y-%m-%d"),
            'tags': self.get_tags()
        }

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag1 = db.Column(db.String(50), nullable=False)
    tag2 = db.Column(db.String(50), nullable=False)
    min_days = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'tag1': self.tag1,
            'tag2': self.tag2,
            'minDays': self.min_days
        }

def check_rule(rule, events, new_event):
    new_event_tags = set(new_event.get_tags())
    for event in events:
        event_tags = set(event.get_tags())
        if (set(rule.tag1.split(',')).intersection(new_event_tags) and
            set(rule.tag2.split(',')).intersection(event_tags)) or \
           (set(rule.tag2.split(',')).intersection(new_event_tags) and
            set(rule.tag1.split(',')).intersection(event_tags)):
            days_between = abs((new_event.date - event.date).days)
            if days_between < rule.min_days:
                return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET', 'POST'])
def handle_events():
    if request.method == 'GET':
        events = Event.query.all()
        return jsonify([event.to_dict() for event in events])
    elif request.method == 'POST':
        data = request.json
        new_event = Event(title=data['title'], date=datetime.strptime(data['date'], "%Y-%m-%d"))
        new_event.set_tags(data['tags'])
        rules = Rule.query.all()
        if all(check_rule(rule, Event.query.all(), new_event) for rule in rules):
            db.session.add(new_event)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Event added successfully', 'event': new_event.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Event addition failed due to rule violation'}), 400

@app.route('/events/<int:event_id>', methods=['PUT', 'DELETE'])
def update_or_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'PUT':
        data = request.json
        event.title = data.get('title', event.title)
        event.date = datetime.strptime(data.get('date', event.date.strftime("%Y-%m-%d")), "%Y-%m-%d")
        if 'tags' in data:
            event.set_tags(data['tags'])
        rules = Rule.query.all()
        if all(check_rule(rule, Event.query.filter(Event.id != event_id).all(), event) for rule in rules):
            db.session.commit()
            return jsonify({'success': True, 'message': 'Event updated successfully', 'event': event.to_dict()})
        else:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Event update failed due to rule violation'}), 400
    elif request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event deleted successfully'})

@app.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'GET':
        rules = Rule.query.all()
        return jsonify([rule.to_dict() for rule in rules])
    elif request.method == 'POST':
        data = request.json
        new_rule = Rule(tag1=data['tag1'], tag2=data['tag2'], min_days=data['minDays'])
        db.session.add(new_rule)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Rule added successfully', 'rule': new_rule.to_dict()})

@app.route('/rules/<int:rule_id>', methods=['PUT', 'DELETE'])
def update_or_delete_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    if request.method == 'PUT':
        data = request.json
        rule.tag1 = data.get('tag1', rule.tag1)
        rule.tag2 = data.get('tag2', rule.tag2)
        rule.min_days = data.get('minDays', rule.min_days)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Rule updated successfully', 'rule': rule.to_dict()})
    elif request.method == 'DELETE':
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Rule deleted successfully'})

@app.route('/process_rule', methods=['POST'])
def process_rule():
    natural_language_rule = request.json['rule']
    
    # Use the NLP pipeline to classify the rule
    result = nlp_pipeline(natural_language_rule)[0]
    
    # This is a simplified interpretation. You'd need to implement more sophisticated parsing
    # based on your specific requirements and model output
    if result['label'] == 'POSITIVE':
        # Assume positive sentiment means the rule is about keeping distance between workouts
        words = natural_language_rule.lower().split()
        tag1 = words[words.index('between') + 1]
        tag2 = words[words.index('and') + 1]
        min_days = next(word for word in words if word.isdigit())
    else:
        # Handle negative sentiment or implement more nuanced parsing
        return jsonify({'success': False, 'message': 'Unable to interpret rule'}), 400

    # Create and save the rule
    new_rule = Rule(tag1=tag1, tag2=tag2, min_days=int(min_days))
    db.session.add(new_rule)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Rule added successfully', 'rule': new_rule.to_dict()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)