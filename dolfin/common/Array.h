// Copyright (C) 2009-2010 Garth N. Wells.
// Licensed under the GNU LGPL Version 2.1.
//
// Modified by Anders Logg, 2010.
//
// First added:  2009-12-06
// Last changed: 2010-04-30

#ifndef __DOLFIN_ARRAY_H
#define __DOLFIN_ARRAY_H

#include <sstream>
#include <string>
#include <utility>
#include <boost/shared_array.hpp>

#include <dolfin/common/types.h>
#include <dolfin/log/dolfin_log.h>
#include "NoDeleter.h"

namespace dolfin
{

  /// This class provides a simple wrapper for a pointer to an array. A purpose
  /// of this class is to enable the simple and safe exchange of data between
  /// C++ and Python.

  template <class T> class Array
  {
  public:

    // Create empty array
    Array() : _size(0), x(0) {}

    /// Create array of size N
    explicit Array(uint N) : _size(N), x(new T[N]) {}

    /// Copy constructor (arg name need to have a different name that 'x')
    Array(const Array& other) : _size(0), x(0)
    { *this = other; }

    /// Construct array from a shared pointer
    Array(uint N, boost::shared_array<T> x) : _size(N), x(x) {}

    /// Construct array from a pointer. Array will not take ownership.
    Array(uint N, T* x) : _size(N), x(boost::shared_array<T>(x, NoDeleter<T>())) {}

    /// Destructor
    ~Array() {}

    /// Assignment operator
    const Array& operator= (const Array& x)
    {
      _size = x._size;
      this->x = x.x;
      return *this;
    }

    /// Construct array from a pointer. Array will not take ownership.
    void update(uint N, T* _x)
    {
      _size = N;
      x.reset(_x, NoDeleter<T>());
    }

    /// Return informal string representation (pretty-print)
    std::string str(bool verbose) const
    {
      std::stringstream s;
      if (verbose)
        warning("Verbose output for Array<Y> not implemented.");
      s << "<Array<T> of size " << size() << ">";
      return s.str();
    }

    /// Resize array to size N. If size changes, contents will be destroyed.
    void resize(uint N)
    {
      if (N == _size)
        return;
      else
      {
        // FIXME: Do we want to allow resizing of shared data?
        if (x.unique())
        {
          _size = N;
          x.reset(new T[N]);
        }
        else
          error("Cannot resize Array. Data is shared");
      }
    }

    /// Return size of array
    uint size() const
    { return _size; }

    /// Zero array
    void zero()
    { std::fill(x.get(), x.get() + _size, 0.0); }

    /// Return minimum value of array
    T min() const
    { return *std::min_element(x.get(), x.get() + _size); }

    /// Return maximum value of array
    T max() const
    { return *std::max_element(x.get(), x.get() + _size);  }

    /// Access value of given entry (const version)
    const T& operator[] (uint i) const
    { assert(i < _size); return x[i]; }

    /// Access value of given entry (non-const version)
    T& operator[] (uint i)
    { assert(i < _size); return x[i]; }

    /// Return pointer to data (const version)
    const boost::shared_array<T> data() const
    { return x; }

    /// Return pointer to data (non-const version)
    boost::shared_array<T> data()
    { return x; }

  private:

    // Length of array
    dolfin::uint _size;

    // Array data
    boost::shared_array<T> x;

  };

}

#endif
