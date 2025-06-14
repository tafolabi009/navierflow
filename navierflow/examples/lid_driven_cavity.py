import numpy as np
import matplotlib.pyplot as plt
from navierflow.core.physics.fluid import FluidFlow
from navierflow.core.numerics.solver import Solver
from navierflow.core.mesh.generation import MeshGenerator
from navierflow.visualization.renderer import Renderer, VisualizationConfig
from navierflow.utils.logging import SimulationLogger
from navierflow.utils.errors import ErrorHandler
from navierflow.utils.validation import Validator
from navierflow.utils.performance import PerformanceMonitor
from navierflow.configs.settings import ConfigManager, SimulationConfig

def main():
    # Initialize logger
    logger = SimulationLogger(
        log_file="lid_driven_cavity.log",
        level="INFO",
        stream=True
    )
    
    # Initialize error handler
    handler = ErrorHandler()
    
    # Initialize validator
    validator = Validator()
    
    # Initialize performance monitor
    monitor = PerformanceMonitor()
    
    # Initialize config manager
    config = SimulationConfig(
        physics={
            "density": 1.0,
            "viscosity": 0.1,
            "gravity": (0.0, 0.0, 0.0)
        },
        numerical={
            "method": "explicit",
            "time_step": 0.001,
            "max_steps": 1000,
            "tolerance": 1e-6
        },
        mesh={
            "type": "structured",
            "dimension": 2,
            "resolution": (100, 100)
        },
        boundary={
            "type": "no_slip",
            "value": 0.0
        },
        output={
            "path": "output",
            "format": "vtk",
            "frequency": 100
        },
        parallel={
            "backend": "cpu",
            "n_processes": 4,
            "n_threads": 2,
            "use_gpu": False
        },
        visualization={
            "type": "surface",
            "colormap": "viridis",
            "background_color": "white",
            "show_axes": True,
            "show_grid": False,
            "show_legend": True,
            "show_colorbar": True,
            "window_size": (800, 600),
            "dpi": 100,
            "animation_fps": 30,
            "animation_duration": 10.0
        }
    )
    
    manager = ConfigManager(config)
    
    try:
        # Start simulation
        logger.start_simulation("Lid-driven cavity flow simulation started")
        
        # Create output directory
        manager.create_output_dir()
        
        # Initialize mesh generator
        with monitor.measure_time("mesh_generation"):
            mesh = MeshGenerator(
                mesh_type="structured",
                dimension=2,
                resolution=(100, 100)
            )
            
            # Generate mesh
            mesh = mesh.generate_structured_mesh(
                bounds=((0, 0), (1, 1)),
                periodic=(False, False)
            )
            
        # Initialize fluid flow
        fluid = FluidFlow(
            density=1.0,
            viscosity=0.1,
            gravity=(0.0, 0.0, 0.0)
        )
        
        # Initialize solver
        solver = Solver(
            method="explicit",
            time_step=0.001,
            max_steps=1000,
            tolerance=1e-6
        )
        
        # Initialize renderer
        renderer = Renderer(VisualizationConfig(
            type="surface",
            colormap="viridis",
            background_color="white",
            show_axes=True,
            show_grid=False,
            show_legend=True,
            show_colorbar=True,
            window_size=(800, 600),
            dpi=100,
            animation_fps=30,
            animation_duration=10.0
        ))
        
        # Initial condition
        velocity = np.zeros((100, 100, 2))
        velocity[-1, :, 0] = 1.0  # Lid velocity
        
        # Solve
        with monitor.measure_time("solving"):
            solution = solver.solve(velocity)
            
        # Compute pressure
        with monitor.measure_time("pressure_computation"):
            pressure = fluid.compute_pressure(solution)
            
        # Compute vorticity
        with monitor.measure_time("vorticity_computation"):
            vorticity = fluid.compute_vorticity(solution)
            
        # Compute strain rate
        with monitor.measure_time("strain_rate_computation"):
            strain_rate = fluid.compute_strain_rate(solution)
            
        # Compute energy
        with monitor.measure_time("energy_computation"):
            energy = fluid.compute_energy(solution)
            
        # Validate results
        with monitor.measure_time("validation"):
            # Validate pressure
            validator.validate_parameter(
                name="pressure",
                value=pressure.mean(),
                expected=0.0,
                tolerance=1e-6
            )
            
            # Validate vorticity
            validator.validate_parameter(
                name="vorticity",
                value=vorticity.mean(),
                expected=0.0,
                tolerance=1e-6
            )
            
            # Validate strain rate
            validator.validate_parameter(
                name="strain_rate",
                value=strain_rate.mean(),
                expected=0.0,
                tolerance=1e-6
            )
            
            # Validate energy
            validator.validate_parameter(
                name="energy",
                value=energy.mean(),
                expected=0.5,
                tolerance=1e-6
            )
            
        # Render results
        with monitor.measure_time("visualization"):
            # Render pressure
            renderer.render_surface(mesh, pressure, "Pressure")
            renderer.save_plot("pressure.png")
            
            # Render vorticity
            renderer.render_surface(mesh, vorticity[..., 0], "Vorticity")
            renderer.save_plot("vorticity.png")
            
            # Render strain rate
            renderer.render_surface(mesh, strain_rate[..., 0, 0], "Strain Rate")
            renderer.save_plot("strain_rate.png")
            
            # Render energy
            renderer.render_surface(mesh, energy, "Energy")
            renderer.save_plot("energy.png")
            
        # Generate summary
        with monitor.measure_time("summary_generation"):
            # Log summary
            logger.log_message("Simulation completed successfully")
            logger.log_message(f"Best pressure: {pressure.min():.6f}")
            logger.log_message(f"Best vorticity: {vorticity.min():.6f}")
            logger.log_message(f"Best strain rate: {strain_rate.min():.6f}")
            logger.log_message(f"Best energy: {energy.min():.6f}")
            
            # Generate validation summary
            validation_summary = validator.generate_summary()
            logger.log_message(f"Validation summary: {validation_summary}")
            
            # Generate performance summary
            performance_summary = monitor.generate_summary()
            logger.log_message(f"Performance summary: {performance_summary}")
            
        # End simulation
        logger.end_simulation(True, "Simulation completed successfully")
        
    except Exception as e:
        # Handle error
        handler.handle_error(
            str(e),
            severity="ERROR",
            context={"simulation": "lid_driven_cavity"}
        )
        
        # Log error
        logger.log_message(f"Error: {str(e)}", level="ERROR")
        
        # End simulation
        logger.end_simulation(False, "Simulation failed")
        
    finally:
        # Cleanup
        renderer.cleanup()
        manager.cleanup_output_dir()
        
if __name__ == "__main__":
    main() 