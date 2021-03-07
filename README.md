# TauCeti Presetsystem
 Presetsystem for touchdesigner

Complete Refactoring of the TauCeti Preset-System and incompatible with the Version2 releases.

Stack and Presets are now persistent based on DAT-Tables. This might reduce speed but increased readability and portability.
Presets can be exported as toxes instead of JSON and get directly edited in the COMP (if you like).

Tagging got removed. It is advised to instead use one presetManager per "instance" instead of one for all with tagging.

Tweener now is complety seperate running on root level for all managers and other components using the tweener.

Dashboard is not simply consistent by also using tables with some cleanupmethods for renaming and removing of presets.
Recorded components now get a a light tagging with a short UUID based on the name defined in the dashboard.
