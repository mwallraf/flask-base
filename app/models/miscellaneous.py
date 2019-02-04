from .. import db
import json
from config import Config


class BaseModelWithOptions(db.Model):

    __abstract__ = True


    def extract_options(self, prepend="option_"):
        """
        Adds "option_" to each individual option and returns
        a dict
        """
        opts = {}
        try:
            opts = json.loads(self.options)
        except:
            pass
        return { "{}{}".format(prepend, key): opts.get(key, "") for key in self.get_options() }


    def extract_facts(self, prepend="fact_"):
        """
        Adds "fact_<fact>_" to each individual fact key and returns
        a dict
        Facts are a dict of dicts
        """
        facts = {}
        rc = {}
        try:
            facts = json.loads(self.options)
        except:
            pass
        for fact in self.get_facts():
            for fact_key in facts.get(fact, {}):
                rc["{}{}_{}".format(prepend, fact, factkey)] = facts[fact][fact_key]
        return rc


    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return []

    @classmethod
    def get_facts(cls):
        """
        Returns the individual facts that can be used in the facts field
        In order that should be displayed in HTML
        """
        return []

    @property
    def is_visible(self):
        return not (hasattr(self, 'hidden') and self.hidden)

    @property
    def is_enabled(self):
        return not (hasattr(self, 'enabled') and self.enabled)

    @property
    def is_required(self):
        return not (hasattr(self, 'required') and self.required)

    def get_option(self, option):
        """
        Return the value of the option if exists,
            otherwise retun empty string
        """
        rc = ""
        try:
            rc = json.loads(self.options).get(option, "")
        except:
            pass
        return rc

    def get_fact(self, fact):
        """
        Return the value of the fact if exists,
            otherwise return empty dict
        """
        rc = ""
        try:
            rc = json.loads(self.facts).get(fact, {})
        except:
            pass
        return rc


    def sanitize_key(self, k):
        """
        Sanitize keys before importing them in the database
        """
        try:
            for c in [ '$' ]:
                k = k.replace(c, "_")
        except:
            pass

        return k


    def serialize_json(self, jsonformat=True, allownull=True, showid=False):
        """
        Returns a serialized format of a record.
        jsonformat: if True then return json text otherwise return dict
        allownull: if True then return everything, otherwise only keys with values
        showid: if True then the id field will be included, otherwise skipped
        """
        o = {}
        for key, required in self.serialize_keys:

            # only id field if required
            if key == "id" and not showid:
                continue

            v = getattr(self, key)
            t = str(type(v))
            #print("key, type = {}, {}".format(key, t))

            # if we don't want empty values then don't store the key
            if not allownull and not v and not required:
                continue

            # if the key is a reference to another model then either return a single value
            # or the entire serialized model (depending on the key)
            if 'app.models.inventory' in t and key == "site":
                if jsonformat:
                    o["siteid"] = self.site.siteid if self.site else ""
                else:
                    o["site"] = self.site.serialize_json(jsonformat, allownull, showid)
                continue
            if 'app.models.inventory' in t and key == "customer":
                o["customer"] = self.customer.name if self.customer else ""
                continue

            # options and facts are json representations in the DB we have to convert it 
            if key in ["options", "facts"]:
                o[key] = json.loads(v) if v else {}

                # for the facts, check INVENTORY_ENABLED_FACTS and make sure for these
                # a key ["fact"]["validated"] exists
                if key == "facts":
                    for enabled_fact, fact_icon in Config.INVENTORY_ENABLED_FACTS:
                        o[key].setdefault(enabled_fact, {})
                        o[key][enabled_fact].setdefault("validated", False)
            else:
                o[key] = v

        if jsonformat:
            return json.dumps(o)
        else:
            return o



class EditableHTML(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    editor_name = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

    @staticmethod
    def get_editable_html(editor_name):
        editable_html_obj = EditableHTML.query.filter_by(
            editor_name=editor_name).first()

        if editable_html_obj is None:
            editable_html_obj = EditableHTML(editor_name=editor_name, value='')
        return editable_html_obj

