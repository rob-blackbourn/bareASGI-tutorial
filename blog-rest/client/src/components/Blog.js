import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import { Link } from 'react-router-dom'
import Typography from '@material-ui/core/Typography'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction'
import IconButton from '@material-ui/core/IconButton'
import DeleteIcon from '@material-ui/icons/Delete'
import EditIcon from '@material-ui/icons/Edit'

const styles = theme => ({
  root: {
  }
})

class Blog extends React.Component {
  state = {
    posts: []
  }

  handleDelete = id => {
    const url = `http://localhost:9501/blog/api/blog_entry/${id}`
    fetch(url, {
      method: 'DELETE'
    })
      .then(request => {
        if (request.ok) {
          this.fetchPosts()
        } else {
          console.log('Failed')
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  fetchPosts = () => {
    fetch('http://localhost:9501/blog/api/blog_entry')
      .then(response => {
        if (response.ok) {
          response.json()
            .then(posts => {
              this.setState({ posts })
            })
            .catch(error => {
              console.log(error)
            })
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  componentDidMount () {
    this.fetchPosts()
  }

  render () {
    const { classes } = this.props
    const { posts } = this.state

    return (
      <div className={classes.root}>
        <Typography variant='h1'>Blog</Typography>

        <List>
          {posts.map(post => (
            <ListItem key={post.id} button component={props => <Link to={`/blog/ui/read/${post.id}`} {...props} />}>
              <ListItemText primary={post.title} secondary={post.description} />
              <ListItemSecondaryAction>
                <IconButton edge='end' aria-label='edit' component={props => <Link to={`/blog/ui/update/${post.id}`} {...props} />}>
                  <EditIcon />
                </IconButton>
                <IconButton edge='end' aria-label='delete' onClick={() => this.handleDelete(post.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        <Link to='/blog/ui/create'>Create a new post</Link>

      </div>
    )
  }
}

Blog.apply.propTypes = {
  classes: PropTypes.object.isRequired
}

export default withStyles(styles)(Blog)
