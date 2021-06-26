import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.constants import (
    INTENT,
    INTENT_RESPONSE_KEY,
    RESPONSE_IDENTIFIER_DELIMITER,
    ACTION_NAME,
    TEXT
)

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class ArabicNumeric(Component):
    """A new component"""

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    supported_language_list = None

    # Defines what language(s) this component can NOT handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one."""
        pass

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.process`
        of components previous to this one."""
        print("Here")
        msg = message.get(TEXT)
        print("Message", msg)
        message.set(TEXT, "1", add_to_output=True)
        # if "١" in msg:
        #     print("Here 1")
        #     msg.replace("١", "1")
        #     print("Message after replace: ", msg)
        #     message.set(TEXT, msg)
        # try:
        #     msg = message.get(TEXT)
        #     print("msg: ", msg)
        #     if "٠" in msg:
        #         msg.replace(".", "0")
        #         message.set(TEXT, msg)
        #     if "١" in msg:
        #         print("Here 1")
        #         msg.replace("١", "1")
        #         print("Message after replace: ", msg)
        #     message.set(TEXT, msg)
        #     if "٢" in msg:
        #         msg.replace("٢", "2")
        #     message.set(TEXT, msg)
        #     if "٣" in msg:
        #         msg.replace("٣", "3")
        #     message.set(TEXT, msg)
        #     if "٤" in msg:
        #         msg.replace("٤", "4")
        #     message.set(TEXT, msg)
        #     if "٥" in msg:
        #         msg.replace("٥", "5")
        #     message.set(TEXT, msg)
        #     if "٦" in msg:
        #         msg.replace("٦", "6")
        #     message.set(TEXT, msg)
        #     if "٧" in msg:
        #         msg.replace("٧", "7")
        #     message.set(TEXT, msg)
        #     if "٨" in msg:
        #         msg.replace("٨", "8")
        #     message.set(TEXT, msg)
        #     if "٩" in msg:
        #         msg.replace("٩", "9")
        #     message.set(TEXT, msg)
        # except Exception as e:
        #     print("Exception", e)


    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""

        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)
