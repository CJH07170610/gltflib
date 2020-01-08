import struct
import operator
from gltflib import (
    GLTF, GLTFModel, Asset, Scene, Node, Mesh, Primitive, Attributes, Buffer, BufferView, Accessor, AccessorType,
    BufferTarget, ComponentType, Base64Resource, GLBResource, FileResource)

class GltfExporter:

    def __init__(self):
        self.model = GLTFModel(asset=Asset(version='2.0',copyright="RBCCE",generator="RBOCC"),
                               scenes=[],
                               nodes=[],
                               meshes=[],
                               buffers=[],
                               bufferViews=[],
                               accessors=[])
        self.resources = []

    def _Tesselateor(self, shape, mesh_quality=1.0):
        from OCC.Core.Visualization import Tesselator
        tess = Tesselator(shape)
        tess.Compute(compute_edges=False,
                     mesh_quality=mesh_quality,
                     uv_coords=False,
                     parallel=True)
        vertices = []
        for i in range(0, tess.ObjGetVertexCount()):
            vertices.append(tess.GetVertex(i))
        normals = []
        for i in range(0, tess.ObjGetNormalCount()):
            normals.append(tess.GetNormal(i))
        triangles = []
        for i in range(0, tess.ObjGetTriangleCount()):
            triangles.append(tess.GetTriangleIndex(i))

        return (vertices, normals, triangles)

    def _ApeendBuffer(self):
        buffer = Buffer()
        self.model.buffers.append(buffer)
        bufferid = len(self.model.buffers)-1
        return buffer, bufferid
    def _ApeendBufferView(self,buffer):
        bufferView = BufferView(buffer=buffer)
        self.model.bufferViews.append(bufferView)
        bufferViewId = len(self.model.bufferViews)-1
        return bufferView, bufferViewId
    def _AppendAccessor(self,bufferView):
        accessor = Accessor(bufferView=bufferView)
        self.model.accessors.append(accessor)
        accessorId = len(self.model.accessors)-1
        return accessor, accessorId
    def _AddMesh(self, vertices, normals, triangles):
        buffer,bufferid=self._ApeendBuffer()
        bufferView1,bufferViewId1=self._ApeendBufferView(bufferid)
        bufferView2,bufferViewId2=self._ApeendBufferView(bufferid)
        bufferView3,bufferViewId3=self._ApeendBufferView(bufferid)
        chunk = b""
        pack = "<HHH"
        for v in triangles:
            chunk += struct.pack(pack, *v)
        bufferView1.byteOffset = 0
        byte_length = bufferView1.byteLength = len(chunk)
        bufferView1.target = BufferTarget.ELEMENT_ARRAY_BUFFER.value
        pack = "<fff"
        for v in normals:
            chunk += struct.pack(pack, *v)
        bufferView2.byteOffset = byte_length
        bufferView2.byteLength = len(chunk)-byte_length
        bufferView2.target = BufferTarget.ARRAY_BUFFER.value
        byte_length = len(chunk)
        for v in vertices:
            chunk += struct.pack(pack, *v)
        bufferView3.byteOffset = byte_length
        bufferView3.byteLength = len(chunk)-byte_length
        bufferView3.target = BufferTarget.ARRAY_BUFFER.value
        resource = Base64Resource(chunk)
        self.resources.append(resource)
        buffer.uri=resource.uri
        buffer.byteLength=len(chunk)
        accessor1,accessorId1=self._AppendAccessor(bufferViewId1)
        accessor1.byteOffset = 0
        accessor1.componentType = ComponentType.UNSIGNED_SHORT.value
        accessor1.count = len(triangles)*3
        accessor1.type = AccessorType.SCALAR.value
        accessor1.max = [3]
        accessor1.min = [0]
        accessor2,accessorId2=self._AppendAccessor(bufferViewId2)
        accessor2.byteOffset = 0
        accessor2.componentType = ComponentType.FLOAT.value
        accessor2.count = len(normals)
        accessor2.type = AccessorType.VEC3.value
        accessor2.max = [1, 1, 1]
        accessor2.min = [0, 0, 0]
        accessor3,accessorId3=self._AppendAccessor(bufferViewId3)
        accessor3.byteOffset = 0
        accessor3.componentType = ComponentType.FLOAT.value
        accessor3.count = len(vertices)
        accessor3.type = AccessorType.VEC3.value
        accessor3.max = [1, 1, 1]
        accessor3.min = [0, 0, 0]
        primitive=Primitive(
             attributes=Attributes(NORMAL=accessorId2,POSITION=accessorId3),indices=accessorId1)
        mesh=Mesh(primitives=[primitive])
        self.model.meshes.append(mesh)
        meshid=len(self.model.meshes)-1
        return mesh,meshid

    def AddShape(self, shape, mesh_quality=1.0):
        # 三角剖分
        vertices, normals, triangles = self._Tesselateor(shape, mesh_quality)
        meshid=self._AddMesh(vertices,normals,triangles)[1]
        node=Node()
        node.mesh=meshid
        self.model.nodes.append(node)
        return node

    def Save(self, filename):
        if len(self.model.scenes)==0:
            scene=Scene(name="Root",nodes=[i for i in range(0,len(self.model.nodes))])
            self.model.scenes.append(scene)
            self.model.scene=0
        gltf = GLTF(model=self.model, resources=self.resources)
        gltf.export(filename)