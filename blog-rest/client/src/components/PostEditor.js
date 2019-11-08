import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import { Link } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'

const styles = theme => ({
  root: {},
  titleTextField: {
    width: 400
  },
  descriptionTextField: {
    width: 400
  },
  contentTextField: {
    width: 400
  },
  submitButton: {
    margin: theme.spacing(2)
  }
})

const PostEditor = props => {
  const {
    classes,
    title,
    onTitleChange,
    description,
    onDescriptionChange,
    content,
    onContentChange,
    onSubmit,
    submitContent
  } = props

  return (
    <div className={classes.root}>
      <Grid container>
        <Grid item xs={12}>
          <TextField
            className={classes.titleTextField}
            label='Title'
            value={title}
            onChange={event => onTitleChange(event.target.value)}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            className={classes.descriptionTextField}
            label='Description'
            value={description}
            onChange={event => onDescriptionChange(event.target.value)}
            multiline
            rows={2}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            className={classes.contentTextField}
            label='Content'
            value={content}
            onChange={event => onContentChange(event.target.value)}
            multiline
            rows={20}
          />
        </Grid>
        <Grid item xs={12}>
          <Button className={classes.submitButton} onClick={onSubmit}>
            {submitContent}
          </Button>
        </Grid>
      </Grid>

      <Link to='/blog/ui/index'>Home</Link>
    </div>
  )
}

PostEditor.propTypes = {
  classes: PropTypes.object.isRequired,
  title: PropTypes.string.string,
  onTitleChange: PropTypes.func.isRequired,
  description: PropTypes.string.string,
  onDescriptionChange: PropTypes.func.isRequired,
  content: PropTypes.string.string,
  onContentChange: PropTypes.func.isRequired,
  submitContent: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default withStyles(styles)(PostEditor)
