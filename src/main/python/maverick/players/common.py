#!/usr/bin/python

"""common.py: Common code for gameplay interfaces"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging
import random
import time

from maverick.client import MaverickClient
from maverick.client import MaverickClientException
from maverick.server import ChessBoard
from maverick.server import ChessMatch

# TODO (mattsh): put more logging throughout this class


class MaverickPlayer(MaverickClient):
    """Provides basic methods for a Maverick AI"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.common.MaverickPlayer")
    logging.basicConfig(level=logging.INFO)

    SLEEP_TIME = 1
    """Amount of time to wait between requests when polling"""

    def __init__(self):
        """Initialize a MaverickPlayer

        NOTE: MaverickPlayer.startPlaying must be run to set playerID, gameID,
        and isWhite before the player can make moves"""

        MaverickClient.__init__(self)

        # Default name (should be overridden for a human AI)
        # i.e., MaverickAI.1234901234.12839429834
        self.name = ".".join([self.__class__.__name__,
                              str(time.time()),
                              str(random.randrange(1, 2 ** 30))])

        # These variables must be overridden
        self.playerID = None    # ID for player's system registration
        self.gameID = None      # ID for game that the player is in
        self.isWhite = None     # Is the player white?

    def displayMessage(self, message):
        """Display a message for the user"""
        print(" -- {0}".format(message))

    def startPlaying(self):
        """Enters the player into an ongoing game (blocks until successful)

        @precondition: self.name must be set"""
        self.playerID = self.request_register(self.name)
        self.gameID = self.request_joinGame(self.playerID)

        # Block until game has started
        while self.request_getStatus() == ChessMatch.STATUS_PENDING:
            self.displayMessage("Waiting until the game starts")
            time.sleep(MaverickPlayer.SLEEP_TIME)

        # NOTE: Player is now in a game that is not pending

        if self.request_getState()["youAreColor"] == ChessBoard.WHITE:
            self.isWhite = True
        else:
            self.isWhite = False

    def run(self):
        """TODO (mattsh) method comment"""
        self.initName()
        self.startPlaying()
        self.welcomePlayer()

        # While the game is in progress
        while self.request_getStatus() == ChessMatch.STATUS_ONGOING:

            # Wait until it is your turn
            while self.request_getState()['isWhitesTurn'] != self.isWhite:
                self.displayMessage("Waiting until turn")

                # Break if a game is stopped while waiting
                if self.request_getStatus() != ChessMatch.STATUS_ONGOING:
                    break

                time.sleep(MaverickPlayer.SLEEP_TIME)

            curBoard = self.request_getState()["board"]
            nextMove = self.getNextMove(curBoard)
            (fromRank, fromFile, toRank, toFile) = nextMove

            try:
                self.request_makePly(fromRank, fromFile, toRank, toFile)
            except MaverickClientException, msg:
                self.handleBadMove(msg, curBoard,
                                   fromRank, fromFile,
                                   toRank, toFile)

        # When this is reached, game is over
        status = self.request_getStatus()
        if status == ChessMatch.STATUS_WHITE_WON:
            self.displayMessage("GAME OVER - WHITE WON")
        elif status == ChessMatch.STATUS_BLACK_WON:
            self.displayMessage("GAME OVER - BLACK WON")
        elif status == ChessMatch.STATUS_DRAWN:
            self.displayMessage("GAME OVER - DRAWN")
        elif status == ChessMatch.STATUS_CANCELLED:
            self.displayMessage("GAME CANCELLED")
        else:
            self.displayMessage("ERROR: UNEXPECTED GAME STATUS TRANSITION")

    def initName(self):
        """Figure out the name of the class"""
        raise NotImplementedError("Must be overridden by the extending class")

    def welcomePlayer(self):
        """Display welcome messages if appropriate"""
        raise NotImplementedError("Must be overridden by the extending class")

    def getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    def handleBadMove(self, errMsg, board, fromRank, fromFile, toRank, toFile):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    def request_getStatus(self):
        """TODO (mattsh) __DETAILED__ docstring"""
        return MaverickClient.request_getStatus(self, self.gameID)

    def request_getState(self):
        """TODO (mattsh) __DETAILED__ docstring"""
        return MaverickClient.request_getState(self,
                                               self.playerID, self.gameID)

    def request_makePly(self, fromRank, fromFile, toRank, toFile):
        """TODO (mattsh) __DETAILED__ docstring"""
        MaverickClient.request_makePly(self,
                                       self.playerID, self.gameID,
                                       fromRank, fromFile,
                                       toRank, toFile)


def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
