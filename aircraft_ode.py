class AircraftODE(om.Group):

    def initialize(self):
        self.options.declare('num_nodes', types=int,
                             desc='Number of nodes to be evaluated in the RHS')

    def setup(self):
        nn = self.options['num_nodes']

        self.add_subsystem(name='mass_comp',
                           subsys=MassComp(num_nodes=nn),
                           promotes_inputs=['mass_fuel'])

        self.connect('mass_comp.W_total', 'flight_equilibrium.W_total')

        self.add_subsystem(name='atmos',
                           subsys=USatm1976Comp(num_nodes=nn),
                           promotes_inputs=[('h', 'alt')])

        self.connect('atmos.pres', 'propulsion.pres')
        self.connect('atmos.sos', 'tas_comp.sos')
        self.connect('atmos.rho', 'q_comp.rho')

        self.add_subsystem(name='tas_comp',
                           subsys=TrueAirspeedComp(num_nodes=nn))

        self.connect('tas_comp.TAS',
                     ('gam_comp.TAS', 'q_comp.TAS', 'range_rate_comp.TAS'))

        self.add_subsystem(name='gam_comp',
                           subsys=SteadyFlightPathAngleComp(num_nodes=nn))

        self.connect('gam_comp.gam',
                     ('flight_equilibrium.gam', 'range_rate_comp.gam'))

        self.add_subsystem(name='q_comp',
                           subsys=DynamicPressureComp(num_nodes=nn))

        self.connect(
            'q_comp.q', ('aero.q', 'flight_equilibrium.q', 'propulsion.q'))

        self.add_subsystem(name='flight_equilibrium',
                           subsys=SteadyFlightEquilibriumGroup(num_nodes=nn),
                           promotes_inputs=['aero.*', 'alt'],
                           promotes_outputs=['aero.*'])

        self.connect('flight_equilibrium.CT', 'propulsion.CT')

        self.add_subsystem(name='propulsion', subsys=PropulsionGroup(num_nodes=nn),
                           promotes_inputs=['alt'])

        self.add_subsystem(name='range_rate_comp',
                           subsys=RangeRateComp(num_nodes=nn))

        # We promoted multiple inputs to the group named 'alt'.
        # In order to automatically create a source variable for 'alt', we must specify their units
        # since they have different units in different components.
        self.set_input_defaults('alt', val=np.ones(nn,), units='m')
