import matplotlib.animation as animation

#animation.py

# Animation of the result on the image
def animation_of_result(all_points, ax, robot_size):
    point, = ax.plot([], [], 'bo', markersize=robot_size)  # The size of the point is adjusted to the size of the robot

    # Storing all points
    all_x = [p[0] for segment in all_points for p in segment]
    all_y = [p[1] for segment in all_points for p in segment]

    def init():
        point.set_data([], [])
        return point,

    def update(frame):
        point.set_data(all_x[frame], all_y[frame])
        return point,

    ani = animation.FuncAnimation(ax.figure, update, frames=len(all_x), init_func=init, interval=50, blit=True)
    return ani