#!/bin/bash

# Script para publicar portada-s-index en PyPI usando UV
# Uso: ./publish_uv.sh [test|prod]

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar argumento
MODE=${1:-prod}

if [ "$MODE" != "test" ] && [ "$MODE" != "prod" ]; then
    print_error "Modo inválido. Usa: ./publish_uv.sh [test|prod]"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       PUBLICAR PORTADA-S-INDEX EN PYPI (usando UV)                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

if [ "$MODE" == "test" ]; then
    print_warning "Modo: TestPyPI (prueba)"
else
    print_warning "Modo: PyPI (producción)"
fi

echo ""

# Paso 1: Verificar que estamos en el directorio correcto
print_step "Verificando directorio..."
if [ ! -f "pyproject.toml" ]; then
    print_error "No se encontró pyproject.toml. Ejecuta desde el directorio portada-s-index/"
    exit 1
fi
print_success "Directorio correcto"

# Paso 2: Verificar que uv está instalado
print_step "Verificando UV..."
if ! command -v uv &> /dev/null; then
    print_error "UV no está instalado"
    echo ""
    echo "Instala UV con uno de estos métodos:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  pip install uv"
    echo "  brew install uv  (en macOS)"
    echo ""
    exit 1
fi
print_success "UV instalado: $(uv --version)"

# Paso 3: Limpiar builds anteriores
print_step "Limpiando builds anteriores..."
rm -rf dist/ build/ *.egg-info src/*.egg-info
print_success "Limpieza completada"

# Paso 4: Ejecutar tests
print_step "Ejecutando tests..."
if [ -f "../test_portada_external.py" ]; then
    cd ..
    python3 test_portada_external.py > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Tests pasaron correctamente"
    else
        print_error "Tests fallaron. Revisa el código antes de publicar."
        exit 1
    fi
    cd portada-s-index
else
    print_warning "No se encontraron tests externos, continuando..."
fi

# Paso 5: Construir el paquete con uv
print_step "Construyendo el paquete con UV..."
uv build
if [ $? -eq 0 ]; then
    print_success "Paquete construido exitosamente"
else
    print_error "Error al construir el paquete"
    exit 1
fi

# Paso 6: Verificar el paquete
print_step "Verificando el paquete..."
if command -v twine &> /dev/null; then
    twine check dist/*
    if [ $? -eq 0 ]; then
        print_success "Paquete verificado correctamente"
    else
        print_error "Error en la verificación del paquete"
        exit 1
    fi
else
    print_warning "Twine no instalado, saltando verificación"
    print_warning "Instala con: uv pip install twine"
fi

# Paso 7: Mostrar archivos generados
echo ""
print_step "Archivos generados:"
ls -lh dist/
echo ""

# Paso 8: Confirmar antes de subir
if [ "$MODE" == "prod" ]; then
    echo -e "${YELLOW}⚠ ADVERTENCIA: Vas a subir a PyPI PRODUCCIÓN${NC}"
    echo ""
    read -p "¿Estás seguro de continuar? (escribe 'si' para confirmar): " confirm
    if [ "$confirm" != "si" ]; then
        print_warning "Publicación cancelada"
        exit 0
    fi
fi

# Paso 9: Subir a PyPI usando uv
echo ""
print_step "Subiendo a PyPI con UV..."

if [ "$MODE" == "test" ]; then
    uv publish --publish-url https://test.pypi.org/legacy/
else
    uv publish
fi

if [ $? -eq 0 ]; then
    echo ""
    print_success "¡Paquete publicado exitosamente!"
    echo ""
    
    if [ "$MODE" == "test" ]; then
        echo "Para instalar desde TestPyPI:"
        echo "  uv pip install --index-url https://test.pypi.org/simple/ portada-s-index"
        echo ""
        echo "Ver en: https://test.pypi.org/project/portada-s-index/"
    else
        echo "Para instalar:"
        echo "  uv pip install portada-s-index"
        echo "  # o"
        echo "  pip install portada-s-index"
        echo ""
        echo "Ver en: https://pypi.org/project/portada-s-index/"
    fi
    echo ""
else
    print_error "Error al subir el paquete"
    echo ""
    echo "Si necesitas autenticación, configura tus credenciales:"
    echo "  export UV_PUBLISH_TOKEN=pypi-tu-token-aqui"
    echo ""
    echo "O usa el archivo de configuración:"
    echo "  ~/.pypirc"
    echo ""
    exit 1
fi
