#!/usr/bin/python

"""NetworkServer.py: A simple network API server for Maverick"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"
__status__ = "Development"
__maintainer__ = "Matthew Strax-Haber and James Magnarelli"

from twisted.internet  import protocol, endpoints, reactor
from twisted.protocols import basic as basicProtocols

from TournamentSystem import TournamentSystem

################################################################################
# Code written by Matthew Strax-Haber and James Magnarelli. All Rights Reserved.
################################################################################

"""Default port for server"""
DEFAULT_PORT = 7782
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002

class MaverickProtocol(basicProtocols.LineOnlyReceiver):
    """Protocol for an asynchronous server that administers chess games to clients"""
    _name = "MaverickChessServer"
    _version = "1.0a1"

    # put a TournamentSystem instance here
    _ts = None

    def __init__(self, tournamentSystem):
        """Store a reference to the TournamentSystem backing up this server"""
        MaverickProtocol._ts = tournamentSystem

    def connectionMade(self):
        """When a client connects, provide a welcome message"""
        ## TODO: log connections

        # Print out the server name and version
        #  (e.g., "MaverickChessServer/1.0a1")
        fStr = "{0}/{1} WaitingForRequest" # Template for welcome message
        welcomeMsg = fStr.format(MaverickProtocol._name,
                                 MaverickProtocol._version)
        self.sendLine(welcomeMsg)

    def connectionLost(self, reason=None):
        """When a client disconnects, log it"""
        ## TODO: log disconnections
    
    def lineReceived(self, line):
        """Take input line-by-line and redirect it to the core"""

        ## TODO: JSON-ify
        requestName = line.partition(" ")[0] # Request name (e.g., "REGISTER")
        requestArgs = {"name": line.partition(" ")[2]} ## FIXME: parse arguments
        ## TODO: log requests
        
        # Map of valid request names to
        #  - corresponding TournamentSystem function
        #  - expected arguments
        #  - expected return values (currently unused)
        validRequests = {"REGISTER": (self._ts.register,
                                      {"name"},
                                      {"playerID"}),
                         "JOIN_GAME": (self._ts.joinGame,
                                       {"playerID"},
                                       {"gameID"}),
                         "GET_STATUS": (self._ts.getStatus,
                                        {"playerID", "gameID"},
                                        {"status"}),
                         "GET_STATE": (self._ts.getState,
                                       {"playerID", "gameID"},
                                       {"youAre", "turn", "board", "history"}),
                         "MAKE_PLY": (self._ts.makePly,
                                      {"playerID", "gameID",
                                       "fromRank", "fromFile",
                                       "toRank", "toFile"},
                                      {"status"})}
        
        errMsg = None # If this gets set, there was an error
        if requestName in validRequests.keys():
            (tsCommand, expArgs, _) = validRequests[requestName]
            if expArgs != set(requestArgs.keys()):
                fStr = "Invalid arguments, expected: {0}"
                errMsg = fStr.format(",".join(list(expArgs)))
            else:
                (successP, result) = tsCommand(**requestArgs)
                if successP:
                    response = "SUCCESS {0}".format(str(result))
                if not successP:
                    errMsg = result["error"]
        else:
            errMsg = "Unrecognized verb \"{0}\" in request".format(requestName)
        
        # Respond to the client
        if errMsg == None:
            self.sendLine(response) # Provide client with the response
        else:
            response = "ERROR: {1} [query=\"{0}\"]".format(line, errMsg)
            self.sendLine(response) # Provide client with the error
        
        # Close connection after each request
        self.transport.loseConnection()
        

class MaverickProtocolFactory(protocol.ServerFactory):
    """Provides a MaverickProtocol backed by a TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance"""

    def __init__(self, tournamentSystem):
        """
        Store a reference to the TournamentSystem backing up this server
        """
        self._tournamentSystem = tournamentSystem
        
    def buildProtocol(self, addr):
        """Create an instance of MaverickProtocol"""
        return MaverickProtocol(self._tournamentSystem)

def _main(port):
    """Main method: called when the server code is run"""
    # Initialize a new instance of MaverickCore
    core = TournamentSystem()

    # Run a server on the specified port
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(MaverickProtocolFactory(core))
    reactor.run() #@UndefinedVariable
    
if __name__ == '__main__':
    _main(DEFAULT_PORT)
