
FROM ubuntu:24.04

# Prevent interactive installation prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, GTK4, Cairo, GStreamer, and OpenGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    python3-cairo \
    \
    # GTK4 dependencies
    gir1.2-gtk-4.0 \
    libgtk-4-1 \
    \
    # Cairo and PyGObject build dependencies
    libcairo2 \
    libcairo2-dev \
    libgirepository-2.0-dev \
    pkg-config \
    gcc \
    \
    # GStreamer multimedia support
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-gl \
    gstreamer1.0-x \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    \
    # OpenGL and Mesa graphics
    libgl1 \
    libegl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    libglu1-mesa \
    libgles2 \
    mesa-utils \
    \
    # X11 display libraries
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxrandr2 \
    libxfixes3 \
    libxi6 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

# Create a Python virtual environment
RUN python3 -m venv --system-site-packages /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Set the project directory
WORKDIR /app

# Copy dependencies first for Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all NOXIA project files
COPY . .

# Configure X11 display
ENV GDK_BACKEND=x11

# Run NOXIA
CMD ["python", "main.py"]

## BUILD DOCKER IMAGE
## docker build -t noxia .
## docker run --rm noxia python -c "import gi, cairo, numpy; from OpenGL import GL; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('All dependencies loaded successfully')"