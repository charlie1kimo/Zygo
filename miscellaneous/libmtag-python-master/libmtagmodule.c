#include <Python.h>
#include "structmember.h"

#include <libmtag/mtag.h>

static PyObject *MTagError;

typedef struct {
	PyObject_HEAD;
	PyObject *tag;
	mtag_file_t *c_file;
} File;

typedef struct {
	PyObject_HEAD;
	PyObject *file;
	mtag_tag_t *c_tag;
} Tag;

static PyTypeObject FileType = {
	PyObject_HEAD_INIT(NULL)
};

static PyTypeObject TagType = {
	PyObject_HEAD_INIT(NULL)
};

static void
Tag_dealloc(Tag* self)
{
	self->ob_type->tp_free((PyObject*) self);
}

static int
Tag_init(PyObject *self,
	 PyObject *args,
	 PyObject *kwords)
{
	Tag *c_self;
	PyObject *file;
	const char *tag_id = NULL;
	int create = false;

	c_self = (Tag *) self;

	if (!PyArg_ParseTuple(args, "O|si", &file, &tag_id, &create))
		return -1;

	c_self->file = file;

	if (tag_id)
		c_self->c_tag = mtag_file_get_tag(((File *) file)->c_file, tag_id, create);
	else
		c_self->c_tag = mtag_file_tag(((File *) file)->c_file);

	return 0;
}

static void
each_tag(const char *key,
	 const char *value,
	 void *user_data)
{
	PyObject *py_key;
	PyObject *py_value;
	PyObject *dict;

	if (!key || !value)
		return;

	py_key = Py_BuildValue("s", key);
	py_value = Py_BuildValue("s", value);
	dict = user_data;

	/** @todo some items will be overwritten */
	PyDict_SetItem(dict, py_key, py_value);
}

static PyObject *
Tag_get_all(Tag *self,
	    PyObject *args)
{
	PyObject *dict;
	dict = PyDict_New();

	mtag_tag_for_each(self->c_tag, each_tag, dict);

	return dict;
}

static PyObject *
Tag_get(Tag *self,
	PyObject *args)
{
	const char *key;

	PyArg_ParseTuple(args, "s", &key);

	return Py_BuildValue("s", mtag_tag_get(self->c_tag, key));
}

static PyObject *
Tag_set(Tag *self,
	PyObject *args)
{
	const char *key;
	const char *value;

	PyArg_ParseTuple(args, "ss", &key, &value);

	mtag_tag_set(self->c_tag, key, value);

	Py_INCREF(Py_None);
	return Py_None;
}

static void
File_dealloc(File* self)
{
	mtag_file_free(self->c_file);
	self->ob_type->tp_free((PyObject*) self);
}

static int
File_init(PyObject *self,
	  PyObject *args,
	  PyObject *kwords)
{
	File *c_self;
	const char *c_file_name;

	c_self = (File *) self;

	if (!PyArg_ParseTuple(args, "s", &c_file_name))
		return -1;

	c_self->c_file = mtag_file_new(c_file_name);

	/** @todo raise exception. */
#if 0
	if (!c_self->c_file)
#endif

	return 0;
}

static PyObject *
File_tag (File *self,
	  PyObject *args)
{
	PyObject *tag_id = NULL;
	PyObject *create = NULL;
	PyArg_UnpackTuple(args, "name", 0, 2, &tag_id, &create);

	if (tag_id) {
		PyObject *tag;
		Tag *c_tag;
		tag = (PyObject *) PyObject_New(Tag, &TagType);
		c_tag = (Tag *) tag;
		if (create)
			PyObject_CallMethod(tag, "__init__", "OOO", self, tag_id, create);
		else
			PyObject_CallMethod(tag, "__init__", "OO", self, tag_id);
		if (!c_tag->c_tag) {
			Py_DECREF(tag);
			Py_INCREF(Py_None);
			return Py_None;
		}
		return tag;
	}

	if (!self->tag) {
		PyObject *tag;
		Tag *c_tag;
		tag = (PyObject *) PyObject_New(Tag, &TagType);
		c_tag = (Tag *) tag;
		PyObject_CallMethod(tag, "__init__", "O", self);
		if (!c_tag->c_tag) {
			Py_DECREF(tag);
			Py_INCREF(Py_None);
			return Py_None;
		}
		self->tag = tag;
	}

	Py_INCREF(self->tag);
	return self->tag;
}

static PyObject *
File_save(File *self,
	  PyObject *args)
{
	mtag_file_save(self->c_file);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
File_strip(File *self,
	   PyObject *args)
{
	const char *tag_id = NULL;

	PyArg_ParseTuple(args, "s", &tag_id);

	mtag_file_strip_tag(self->c_file, tag_id);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef File_methods[] = {
	{ "tag", (PyCFunction)File_tag, METH_VARARGS, "Tag." },
	{ "save", (PyCFunction)File_save, METH_NOARGS, "Save." },
	{ "strip", (PyCFunction)File_strip, METH_VARARGS, "Strip Tag." },
	{ NULL }
};

static PyMethodDef Tag_methods[] = {
	{ "get", (PyCFunction)Tag_get, METH_VARARGS, "Get." },
	{ "set", (PyCFunction)Tag_set, METH_VARARGS, "Set." },
	{ "get_all", (PyCFunction)Tag_get_all, METH_NOARGS, "Get All." },
	{ NULL }
};

static PyMethodDef MTagMethods[] = {
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initlibmtag(void)
{
	PyObject *m;

	m = Py_InitModule("libmtag", MTagMethods);

	TagType.tp_new = PyType_GenericNew;
	TagType.tp_name = "Tag";
	TagType.tp_basicsize = sizeof(Tag);
	TagType.tp_dealloc = (destructor) Tag_dealloc;
	TagType.tp_flags = Py_TPFLAGS_DEFAULT;
	TagType.tp_methods = Tag_methods;
	TagType.tp_init = Tag_init;

	FileType.tp_new = PyType_GenericNew;
	FileType.tp_name = "File";
	FileType.tp_basicsize = sizeof(File);
	FileType.tp_dealloc = (destructor) File_dealloc;
	FileType.tp_flags = Py_TPFLAGS_DEFAULT;
	FileType.tp_methods = File_methods;
	FileType.tp_init = File_init;

	if (PyType_Ready(&FileType) < 0)
		return;

	if (PyType_Ready(&TagType) < 0)
		return;

	PyModule_AddObject(m, "Tag", (PyObject *) &TagType);
	PyModule_AddObject(m, "File", (PyObject *) &FileType);

	MTagError = PyErr_NewException("libmtag.error", NULL, NULL);
	Py_INCREF(MTagError);
	PyModule_AddObject(m, "error", MTagError);
}
