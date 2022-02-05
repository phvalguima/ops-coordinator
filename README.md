# ops-coordinator
Distributed lock coordinator for Juju charms units

## Introduction

Implements the BaseCoordinator from Charmhelpers on Operator Framework.

The OpsCoordinator subclasses Serial Coordinator. It masks the use of hookenv
primitives to deal with Juju and exposes Events and methods to the other
elements. This is possible because the BaseCoordinator does not use any of the
default files or unit databases to store its own state. Instead, it saves on
local file named: .charmhelpers.coordinator.OpsCoordinator. Therefore, no
conflicts are expected with the Operator Framework.

Also implements the RestartEvent. This event should be emitted
every time a restart is needed and will trigger the lock negotiation protocol
across the peer relation.

RestartEvent receives two arguments:
ctx: a dictionary containing current context when the RestartEvent was issued.
     this variable is not used in the restart logic itself, it is intended to
     let the user optionally update its own context once the restart has been
     done.
services: a list of strings. It is the list of services to be restarted.

It is important to understand that RestartEvent only restarts systemd services
using the service_restart from Charmhelpers.

There is also an option to add a callback function in the coordinator. That
allows the charm to report back after a restart, e.g. if it needs to share
data across a relation after successful restart.

## How to implement on your charm

The coordinator manages the lock at the beginning and the end of charm's lifecycle.
Add the following to your charm.

```

    from ops_coordinator.ops_coordinator import RestartCharmEvent, OpsCoordinator

    class CharmBaseSubclass(...):

        on = RestartCharmEvent()

        state = StoredState()

        def check_restart_is_valid(self):
            # The goal of this method is to check beyond the service_restart()
            # if the service is actually functional. If yes, then let restart
            # processing follow its normal path and drop the remaining events.
            # Otherwise, it needs to take a different route. In this example,
            # it will simply defer the event, but it could as well abandon
            # it and block the unit with "restart failed", so the operator
            # can be warned and take a counter-measure.

            # ########################
            # Do a check, e.g. try connecting to service endpoint
            # ########################


        def on_restart_event(self, event):

            # OPTIONALLY: depending on how often RestartEvents are emitted,
            #  there is a good chance several of the RestartEvents will be
            #  stacked on top of each other.
            #  One example, that can happen because this unit was waiting
            #  for the lock to be released (if event.restart()) while
            #  processing all the hooks. In this case,
            #  several RestartEvents got stacked for the same lock.
            #  This check will allow to run the first restart event and
            #  discard subsequent events.
            #  The check can be extended to a dictionary if event.services
            #  change and get restarted independently.

            if not self.state.need_restart:
                # Discard all subsequent restart events.
                return

            # This is the logic that processes the restart
            if event.restart():
                # Restart was successful, if the charm is keeping track
                # of a context, that is the place it should be updated
                self.state.config_state = event.ctx

                if self.check_restart_is_valid():
                    # OPTIONALLY, set need_restart:
                    self.state.need_restart = False
                else:
                    # This restart failed at the check, defer it for retrial
                    event.defer()
                    return

            else:
                # defer the RestartEvent as it is still waiting for the
                # lock to be released.
                event.defer()

        ...

        def __init__(self, *args):

            ...

            self.framework.observe(self.on.restart_event,
                                   self.on_restart_event)

            # Coordinator has logic that the leader unit should always run
            # at start of hookenv and at its end. Therefore it should be
            # called in __init__ and __del__, respectively.
            self.coordinator = OpsCoordinator()
            self.coordinator.resume()
            # OPTIONALLY, set a need_restart flag. Check on_restart_event
            # comments to better understand its use.
            self.state.set_default(need_restart=False)

        def __del__(self):
            # Run the atexit hookenv logic
            self.coordinator.release()

        ...

        def on_config_changed(self, event):

            ...

            # Collect the config changes to build a context
            # store it in config_state

            ...

            # Check if restart is needed. A context can be provided to be
            # used in RestartEvent's processing.
            # The self.services is a list of service names that will be
            # restarted.
            if _some_check_to_not_issue_too_many_restarts():
                self.on.restart_event.emit(self.ctx, services=self.services)
                # OPTIONALLY, set a flag that will signal if the process has
                # already restarted or not, check the on_restart_event above.
                self.state.need_restart = True
```
