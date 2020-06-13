from mailer.mail_handler import send_mail
from string import digits
import common_utils
GROCERIES_KEY = "groceries"
PHONE_KEY = "phone"


class Context():
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None

    """
    A reference to the current state of the Context.
    """

    def __init__(self, content, id):
        self.content = content
        self.interseting_input = {}
        self.reset_intersting_input()

        lgm = common_utils.SingletonRotateLoggerManager()
        self.logger = lgm.create_logger(logger_name="session_contents"+str(id))

        self.start_order = \
            StartOrder(self.content,  self.interseting_input)
        self.cancel_order = \
            CancelOrder(self.content,  self.interseting_input)
        self.make_purchase_list = \
            MakePurchaseList(self.content,  self.interseting_input)
        self.additional_purchase_list = \
            AdditionalPucharseList(self.content,  self.interseting_input)
        self.add_phone_before_complete_order = \
            AddPhoneBeforeCompleteOrder(self.content,  self.interseting_input)
        self.complete_order = CompleteOrder(
            self.content,  self.interseting_input)

        self.start_order.add_next_states([self.make_purchase_list])
        self.cancel_order.add_next_states([self.start_order])
        self.make_purchase_list.add_next_states(
            [self.add_phone_before_complete_order, self.cancel_order])
        self.add_phone_before_complete_order.add_next_states(
            [self.additional_purchase_list, self.cancel_order])
        self.additional_purchase_list.add_next_states(
            [self.add_phone_before_complete_order, self.cancel_order])
        self.complete_order.add_next_states([self.start_order])
        self.transition_to(self.start_order)

    def reset_intersting_input(self):
        self.interseting_input[PHONE_KEY] = ""
        self.interseting_input[GROCERIES_KEY] = []

    @property
    def state(self):
        return str(self._state)

    def illegal_input_response(self):
        return self.content.illegal_input_response()

    def is_legal_input(self, input_value):
        return self._state.is_legal_input(input_value)

    def transition_to(self, state):
        """
        The Context allows changing the State object at runtime.
        """

        self._state = state
        self._state.context = self

        if 'CompleteOrder' == repr(state):
            self.interseting_input[GROCERIES_KEY].append(" ")
            send_mail('\r\n'.join(self.interseting_input[GROCERIES_KEY]),
                      self.content.order_from()
                      + " "
                      + self.interseting_input[PHONE_KEY])

    """
    The Context delegates part of its behavior to the current State object.
    """

    def get_state_options_content(self):
        # return self._state.get_options()
        response_dict = self._state.get_options()
        response = self._state.get_content()['Content'] + '\r\n' + '\r\n'
        for order in response_dict.values():
            response += (self.content.for_text()
                         + order['Name']
                         + " "
                         + self.content.press_key()
                         + " "
                         + order['Choice']
                         + '\r\n')
        response += '\r\n'
        return response

    def handle(self, input_value):
        self._state.handle(input_value)


class Content():
    def order_from(self):
        pass

    def for_text(self):
        pass

    def make_order(self):
        pass

    def press_key(self):
        pass

    def change_order(self):
        pass

    def how_may_help(self):
        pass

    def return_on_phone(self):
        pass

    def thanks_msg(self):
        pass

    def order_canaceled(self):
        pass

    def illegal_input_response(self):
        pass

    def start_order(self):
        pass

    def make_prchase_list(self):
        pass

    def order_completion(self):
        pass

    def cancel_order(self):
        pass

    def add_phone(self):
        pass

    def your_order_summary(self):
        pass

    def additional_make_order(sekf):
        pass


class HebrewContent(Content):
    def order_from(self):
        return "הזמנה ממספר טלפון"

    def your_order_summary(self):
        return "סיכום הזמנתך"

    def for_text(self):
        return "ל"

    def make_order(self):
        str = "אנא מלאי את רשימת הקניות שלך כעת"
        return str

    def press_key(self):
        return "שלחי"

    def change_order(self):
        return"לשינוי הזמנה קיימת"

    def start_order(self):
        return "התחלת הזמנה חדשה"

    def how_may_help(self):
        str = "ברוכה הבאה לחנות הירקות שלנו, איך אוכל לעזור?"
        return str

    def return_on_phone(self):
        return "ההזמנה הושלמה והועברה לירקן שיחזור אלייך בטלפון"

    def thanks_msg(self):
        return "תודה"

    def order_canaceled(self):
        return "ההזמנה בוטלה."

    def illegal_input_response(self):
        return "המערכת לא הבינה את הודעתך, אנא נסח מחדש"

    def make_prchase_list(self):
        return "מילוי נוסף של רשימת קניות"

    def order_completion(self):
        return "השלמת ההזמנה"

    def cancel_order(self):
        return "ביטול הזמנה"

    def add_phone(self):
        return "להשלמת הזמנה אנא הכניסי מספר טלפון לחזרה אלייך"

    def additional_make_order(sekf):
        return "כעת תוכלי להוסיף פריטים נוספים לרשימת הקניות"


class State():

    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    def __init__(self, content, interesting_input):
        self.content = content
        self.next_state_options = {}
        self.state_name_to_dict_key = {}
        self.interesting_input = interesting_input

    def add_next_states(self, state_list):
        self.__key_in_dict_of_next_states_by_state_name(state_list)
        self.next_state_options = \
            {str(i): state_list[i]
             for i in range(len(state_list))}

    def __key_in_dict_of_next_states_by_state_name(self, state_list):
        self.state_name_to_dict_key = \
            {repr(state_list[i]): str(i)
             for i in range(len(state_list))}

    def _state_key_by_name(self, name):
        return self.state_name_to_dict_key[name]

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    def get_options(self):
        return_options = {}
        for key in self.next_state_options:
            option_description = {"Choice": str(key)}
            option_description.update(
                self.next_state_options[key].get_content())

            return_options[
                self.next_state_options[key].__repr__()] =  \
                option_description

        return return_options

    def is_legal_input(self, input_value):
        return input_value in self.next_state_options.keys()

    def handle(self, input_value):
        self.context.transition_to(self.next_state_options[input_value])

    def get_content(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass


class StartOrder(State):
    def __init__(self, content, intersting_input):
        super(StartOrder, self).__init__(content, intersting_input)

    def get_content(self):
        return {"Name": self.content.start_order(),
                "Content": self.content.how_may_help()}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__

    def handle(self, input_value):
        self.context.reset_intersting_input()
        self.context.transition_to(self.next_state_options[input_value])


class MakePurchaseList(State):

    def __init__(self,  content, intersting_input):
        super(MakePurchaseList, self).__init__(content, intersting_input)

    def get_content(self):
        return {"Name": self.content.make_prchase_list(),
                "Content": self.content.make_order()}

    def is_legal_input(self, input_value):
        # either its the list of groceries or want to return 'return state'
        return (
            input_value in self.next_state_options.keys()
            or input_value not in digits)

    def handle(self, input_value):
        if input_value not in digits:
            self.interesting_input[GROCERIES_KEY].append(input_value)
            return
        self.context.transition_to(self.next_state_options[input_value])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__


class AdditionalPucharseList(MakePurchaseList):
    def __init__(self,  content, intersting_input):
        super(AdditionalPucharseList, self).__init__(content, intersting_input)

    def get_content(self):
        return {"Name": self.content.make_prchase_list(),
                "Content": self.content.make_order()}

    def is_legal_input(self, input_value):
        # either its the list of groceries or want to return 'return state'
        return (
            input_value in self.next_state_options.keys()
            or input_value not in digits)

    def handle(self, input_value):
        if input_value not in digits:
            self.interesting_input[GROCERIES_KEY].append(input_value)
            return
        self.context.transition_to(self.next_state_options[input_value])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__


class AddPhoneBeforeCompleteOrder(State):
    def __init__(self,  content, intersting_input):
        super(AddPhoneBeforeCompleteOrder, self).__init__(
            content, intersting_input)

    def get_content(self):
        return {"Name": self.content.order_completion(),
                "Content": self.__complete_content()}

    def is_legal_input(self, input_value):
        # either its the phone number or want to return 'return state'
        return (
            input_value in self.next_state_options.keys()
            or input_value not in digits)

    def __complete_content(self):
        response = self.content.add_phone() + '\r\n' + '\r\n'
        response += self.content.your_order_summary() + ':\r\n'
        for line in self.interesting_input[GROCERIES_KEY]:
            response += line + '\r\n'
        response += '\r\n'
        return response

    def handle(self, input_value):
        if input_value not in digits:
            self.interesting_input[PHONE_KEY] = input_value
            self.context.transition_to(self.context.complete_order)
            return
        self.context.transition_to(self.next_state_options[input_value])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__


class CompleteOrder(State):
    def __init__(self,  content, intersting_input):
        super(CompleteOrder, self).__init__(content, intersting_input)

    def get_content(self):
        return {"Name": self.content.order_completion(),
                "Content": self.__complete_content()}

    def __complete_content(self):
        response = self.content.your_order_summary() + ':\r\n'
        for line in self.interesting_input[GROCERIES_KEY]:
            response += line + '\r\n'
        response += '\r\n'
        return (response +
                self.content.return_on_phone()
                + " "
                + self.interesting_input[PHONE_KEY]
                + '\r\n'
                + self.content.thanks_msg()
                + '\r\n')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__


class CancelOrder(State):

    def __init__(self, content, intersting_input):
        super(CancelOrder, self).__init__(content, intersting_input)

    def get_content(self):
        return {"Name": self.content.cancel_order(),
                "Content": self.content.order_canaceled()}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__

    def handle(self, input_value):
        self.context.reset_intersting_input()
        self.context.transition_to(self.next_state_options[input_value])
