Very basic code to support this board in HA:
https://sequentmicrosystems.com/index.php?route=product/product&product_id=50

Doc explaining the dev process in HA:
https://developers.home-assistant.io/docs/development_index

TODO:
- test I2C communication on init, fail if not working
- implement port logic
- lib8relay 1.0.0 needs to be pushed to PyPi!!
https://developers.home-assistant.io/docs/creating_component_code_review/#4-communication-with-devicesservices
https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
Meanwhile, to use it in dev:
https://developers.home-assistant.io/docs/creating_integration_manifest#custom-requirements-during-development--testing
- extend this to other devices/input devices too. I can help.

References:
- good example:
https://github.com/home-assistant/core/tree/dev/homeassistant/components/raspihats
- the end result should live here:
https://github.com/home-assistant/core/tree/dev/homeassistant/components